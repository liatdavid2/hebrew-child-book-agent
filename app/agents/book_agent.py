import json
import os
from typing import Any, Dict, List, TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


class BookState(TypedDict, total=False):
    cover_text: str
    child_age: str
    style_instructions: str
    pages: List[Dict[str, Any]]
    clean_input: Dict[str, Any]
    book: Dict[str, Any]


def normalize_node(state: BookState) -> BookState:
    pages = sorted(state["pages"], key=lambda p: p["page_number"])
    clean = {
        "cover_text": state["cover_text"].strip(),
        "child_age": (state.get("child_age") or "4-7").strip(),
        "style_instructions": (state.get("style_instructions") or "").strip(),
        "pages": [
            {
                "page_number": p["page_number"],
                "text": p["text"].strip(),
            }
            for p in pages
            if p.get("text", "").strip()
        ],
    }
    if not clean["pages"]:
        raise ValueError("At least one page is required.")
    return {"clean_input": clean}


def write_book_node(state: BookState) -> BookState:
    data = state["clean_input"]

    system = """
You are a Hebrew children's book agent.
Create a polished Hebrew children's picture book from the user's cover and page texts.

Rules:
- Hebrew only for title, subtitle, cover_text, page final_text, and Hebrew image prompts.
- Keep the original story idea and page order.
- Improve wording gently.
- Keep short and child-friendly sentences.
- Make it warm, simple, imaginative, and not scary.
- Create exactly one output page for each input page.
- Create one cover image prompt and one image prompt for every page.
- Return valid JSON only.
"""

    payload = {
        "cover_text": data["cover_text"],
        "child_age": data["child_age"],
        "style_instructions": data["style_instructions"],
        "pages": data["pages"],
        "required_json_format": {
            "title": "string",
            "subtitle": "string",
            "cover_text": "string",
            "age_range": "string",
            "style": "string",
            "cover_image_prompt_hebrew": "string",
            "cover_image_prompt_english": "string",
            "pages": [
                {
                    "page_number": 1,
                    "original_text": "string",
                    "final_text": "string",
                    "image_prompt_hebrew": "string",
                    "image_prompt_english": "string"
                }
            ]
        }
    }

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=2)},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    content = response.choices[0].message.content.strip()
    book = json.loads(content)
    return {"book": book}


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
    return book_graph.invoke(payload)["book"]
