
import json
import os
import uuid
import zipfile
from html import escape
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


class PageInput(BaseModel):
    page_number: int = Field(..., ge=1)
    text: str = Field(..., min_length=1)


class BookRequest(BaseModel):
    cover_text: str = Field(..., min_length=1)
    child_age: str = "4-7"
    style_instructions: str = ""
    pages: List[PageInput] = Field(..., min_length=1)


class BookState(TypedDict, total=False):
    cover_text: str
    child_age: str
    style_instructions: str
    pages: List[Dict[str, Any]]
    normalized: Dict[str, Any]
    book: Dict[str, Any]


BOOK_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title": {"type": "string"},
        "subtitle": {"type": "string"},
        "cover_text": {"type": "string"},
        "age_range": {"type": "string"},
        "parent_note": {"type": "string"},
        "pages": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "page_number": {"type": "integer"},
                    "original_text": {"type": "string"},
                    "final_text": {"type": "string"},
                    "image_prompt_hebrew": {"type": "string"},
                    "image_prompt_english": {"type": "string"},
                },
                "required": [
                    "page_number",
                    "original_text",
                    "final_text",
                    "image_prompt_hebrew",
                    "image_prompt_english",
                ],
            },
        },
    },
    "required": ["title", "subtitle", "cover_text", "age_range", "parent_note", "pages"],
}


def normalize_node(state: BookState) -> BookState:
    pages = sorted(state["pages"], key=lambda x: x["page_number"])
    clean_pages = []
    for i, page in enumerate(pages, start=1):
        text = str(page.get("text", "")).strip()
        if text:
            clean_pages.append({"page_number": i, "text": text})

    if not clean_pages:
        raise ValueError("צריך לפחות עמוד אחד עם מלל.")

    return {
        "normalized": {
            "cover_text": state["cover_text"].strip(),
            "child_age": (state.get("child_age") or "4-7").strip(),
            "style_instructions": (state.get("style_instructions") or "").strip(),
            "pages": clean_pages,
        }
    }


def write_book_node(state: BookState) -> BookState:
    data = state["normalized"]

    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "PUT_YOUR_OPENAI_API_KEY_HERE":
        raise ValueError("OPENAI_API_KEY חסר או עדיין placeholder בקובץ .env")

    system_prompt = """
You are a Hebrew children's book agent.

Create a polished Hebrew picture book from the user's inputs.

Rules:
- Hebrew only for story text.
- Preserve the child's original ideas and page order.
- Improve the wording gently, without changing the story into a different story.
- Use short sentences suitable for young children.
- Keep the story warm, simple, imaginative, and child-safe.
- Do not add scary or adult content.
- Create image prompts for every page:
  - Hebrew prompt
  - English prompt for image generation
- Return valid JSON only matching the provided schema.
"""

    user_payload = {
        "cover_text": data["cover_text"],
        "child_age": data["child_age"],
        "style_instructions": data["style_instructions"],
        "pages": data["pages"],
    }

    response = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, indent=2)},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "hebrew_child_book",
                "schema": BOOK_SCHEMA,
                "strict": True,
            }
        },
    )

    return {"book": json.loads(response.output_text)}


def build_graph():
    graph = StateGraph(BookState)
    graph.add_node("normalize", normalize_node)
    graph.add_node("write_book", write_book_node)
    graph.add_edge(START, "normalize")
    graph.add_edge("normalize", "write_book")
    graph.add_edge("write_book", END)
    return graph.compile()


book_graph = build_graph()


def generate_book(payload: Dict[str, Any]) -> Dict[str, Any]:
    result = book_graph.invoke(payload)
    return result["book"]


def build_book_site(book: Dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "book.json").write_text(json.dumps(book, ensure_ascii=False, indent=2), encoding="utf-8")

    pages_html = [
        f"""
        <article class="page is-active">
          <div class="cover">
            <span class="badge">שער</span>
            <h1>{escape(book.get("title", "ספר ילדים"))}</h1>
            <p>{escape(book.get("subtitle", ""))}</p>
            <div class="cover-text">{escape(book.get("cover_text", ""))}</div>
          </div>
        </article>
        """
    ]

    for page in book.get("pages", []):
        pages_html.append(
            f"""
            <article class="page">
              <div class="page-art"><span>איור לעמוד {page.get("page_number", "")}</span></div>
              <div class="page-text">
                <span class="badge">עמוד {page.get("page_number", "")}</span>
                <p>{escape(page.get("final_text", ""))}</p>
              </div>
              <details class="prompt-box">
                <summary>Prompt לתמונה</summary>
                <p>{escape(page.get("image_prompt_english", ""))}</p>
              </details>
            </article>
            """
        )

    index_html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(book.get("title", "ספר ילדים"))}</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <main class="app">
    <section class="book" id="book">
      {''.join(pages_html)}
    </section>
    <nav class="controls">
      <button id="nextBtn" type="button">הבא</button>
      <span id="counter">שער</span>
      <button id="prevBtn" type="button">הקודם</button>
    </nav>
  </main>
  <script src="script.js"></script>
</body>
</html>
"""

    style_css = """*{box-sizing:border-box}:root{--ink:#2b2140;--muted:#6a6078;--purple:#7b43c6;--pink:#e84f9d;--paper:rgba(255,255,255,.92);--shadow:0 24px 70px rgba(41,26,66,.2)}html,body{min-height:100%;margin:0}body{font-family:Arial,"Noto Sans Hebrew",sans-serif;color:var(--ink);background:radial-gradient(circle at 15% 12%,rgba(255,255,255,.95),transparent 28rem),linear-gradient(135deg,#fae8ff,#dff7ff 60%,#fff4d8)}.app{min-height:100svh;display:grid;place-items:center;gap:14px;padding:16px}.book{width:min(94vw,680px);aspect-ratio:4/5.5;position:relative;filter:drop-shadow(var(--shadow))}.page{position:absolute;inset:0;display:none;overflow:hidden;border-radius:28px;background:var(--paper);border:8px solid rgba(255,255,255,.95);padding:clamp(18px,4vw,34px)}.page.is-active{display:grid;align-content:center;gap:18px}.cover{display:grid;gap:16px;text-align:center}.cover h1{margin:0;font-size:clamp(2rem,7vw,4.5rem)}.cover p,.cover-text,.page-text p{margin:0;font-size:clamp(1.2rem,3vw,2rem);line-height:1.65}.cover-text{margin-top:20px;padding:18px;border-radius:22px;background:rgba(123,67,198,.1)}.page-art{min-height:42%;display:grid;place-items:center;border-radius:24px;background:radial-gradient(circle at 30% 20%,rgba(255,255,255,.88),transparent 12rem),linear-gradient(135deg,rgba(232,79,157,.18),rgba(123,67,198,.18));color:var(--purple);font-weight:900;text-align:center}.page-text{display:grid;gap:12px}.badge{justify-self:center;padding:7px 14px;border-radius:999px;background:rgba(123,67,198,.12);color:var(--purple);font-weight:900}.prompt-box{color:var(--muted);font-size:.95rem}.controls{width:min(94vw,680px);display:grid;grid-template-columns:1fr auto 1fr;gap:10px;align-items:center}.controls button{min-height:48px;border:0;border-radius:999px;background:linear-gradient(135deg,var(--pink),var(--purple));color:white;font-weight:900;cursor:pointer}.controls button:disabled{opacity:.38;cursor:not-allowed}#counter{min-width:90px;text-align:center;font-weight:900;color:var(--purple)}@media(max-width:560px){.book{width:96vw;aspect-ratio:4/5.8}.page{border-width:5px;border-radius:22px}}"""
    script_js = """const pages=Array.from(document.querySelectorAll(".page"));const nextBtn=document.getElementById("nextBtn");const prevBtn=document.getElementById("prevBtn");const counter=document.getElementById("counter");let index=0;function update(){pages.forEach((p,i)=>p.classList.toggle("is-active",i===index));prevBtn.disabled=index===0;nextBtn.disabled=index===pages.length-1;counter.textContent=index===0?"שער":`עמוד ${index}`}nextBtn.addEventListener("click",()=>{if(index<pages.length-1){index+=1;update()}});prevBtn.addEventListener("click",()=>{if(index>0){index-=1;update()}});document.addEventListener("keydown",e=>{if(e.key==="ArrowLeft"&&index<pages.length-1){index+=1;update()}if(e.key==="ArrowRight"&&index>0){index-=1;update()}});update();"""

    (output_dir / "index.html").write_text(index_html, encoding="utf-8")
    (output_dir / "style.css").write_text(style_css, encoding="utf-8")
    (output_dir / "script.js").write_text(script_js, encoding="utf-8")

    zip_path = output_dir / "book_site.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in output_dir.rglob("*"):
            if path.is_file() and path.name != "book_site.zip":
                zf.write(path, path.relative_to(output_dir))
    return zip_path


app = FastAPI(title="Hebrew Child Book Agent UI")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")


@app.post("/api/generate-book")
def generate_book_api(request: BookRequest):
    try:
        book = generate_book(request.model_dump())
        book_id = str(uuid.uuid4())[:8]
        output_dir = OUTPUTS_DIR / book_id
        build_book_site(book, output_dir)
        return {"book_id": book_id, "book": book, "download_url": f"/api/download/{book_id}"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/download/{book_id}")
def download_book(book_id: str):
    zip_path = OUTPUTS_DIR / book_id / "book_site.zip"
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Book ZIP not found")
    return FileResponse(zip_path, media_type="application/zip", filename=f"hebrew_child_book_{book_id}.zip")
