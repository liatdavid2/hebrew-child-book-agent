import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.agents.book_agent import generate_book
from app.agents.image_agent import generate_book_images
from app.exporter import build_book_site
from app.models import BookRequest
from app.agents.nikud_agent import add_nikud_to_book

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"
OUTPUTS_DIR = BASE_DIR / "outputs"

app = FastAPI(title="Hebrew Book Agent With Images")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
app.mount("/generated", StaticFiles(directory=OUTPUTS_DIR), name="generated")


@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")


@app.post("/api/generate-book")
def generate_book_api(request: BookRequest):
    try:
        payload = request.model_dump()
        book = generate_book(payload)
        print("1.5. Adding Hebrew niqqud...")
        book = add_nikud_to_book(book)

        book_id = str(uuid.uuid4())[:8]
        output_dir = OUTPUTS_DIR / book_id
        output_dir.mkdir(parents=True, exist_ok=True)

        book = generate_book_images(book, output_dir)
        build_book_site(book, output_dir)

        cover_url = f"/generated/{book_id}/assets/cover.png"
        for idx, page in enumerate(book.get("pages", []), start=1):
            page["preview_image_url"] = f"/generated/{book_id}/assets/page-{idx}.png"

        return {
            "book_id": book_id,
            "book": book,
            "cover_preview_url": cover_url,
            "download_url": f"/api/download/{book_id}",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/download/{book_id}")
def download_book(book_id: str):
    zip_path = OUTPUTS_DIR / book_id / "storybook_html.zip"
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Book ZIP not found")
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"storybook_html_{book_id}.zip",
    )
