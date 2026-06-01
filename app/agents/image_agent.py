import base64
import os
from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
IMAGE_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1024x1536")
IMAGE_QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "high")


def _save_image_from_b64(b64_data: str, out_path: Path) -> None:
    out_path.write_bytes(base64.b64decode(b64_data))


def _generate_png(prompt: str, out_path: Path) -> None:
    request_kwargs = {
        "model": IMAGE_MODEL,
        "prompt": prompt,
        "size": IMAGE_SIZE,
    }

    if IMAGE_QUALITY:
        request_kwargs["quality"] = IMAGE_QUALITY

    try:
        response = client.images.generate(**request_kwargs)
    except Exception as exc:
        message = str(exc).lower()

        if "quality" in message:
            request_kwargs.pop("quality", None)
            response = client.images.generate(**request_kwargs)
        else:
            raise

    data = response.data[0]

    if getattr(data, "b64_json", None):
        _save_image_from_b64(data.b64_json, out_path)
        return

    raise ValueError("Image generation response did not include b64_json.")


def build_image_prompts(book: Dict[str, Any]) -> Dict[str, str]:
    style = book.get("style", "")

    shared_visual_style = (
        "Create a polished children's picture-book illustration. "
        "Beautiful, soft, colorful, warm, whimsical, child-friendly. "
        "Clean composition, high quality digital illustration. "
        "No text inside the image. "
        "No Hebrew letters. "
        "No English letters. "
        "No words. "
        "No captions. "
        "No signs. "
        "No typography. "
        "No book title inside the image. "
        "The written story text will be added later in HTML, so the image must be illustration only. "
        "Keep the same visual style across all pages."
    )

    cover_prompt = (
        "Children's picture-book cover illustration. "
        f"Style: {style}. "
        f"{book.get('cover_image_prompt_english', '')}. "
        f"{shared_visual_style}"
    )

    page_prompts: List[str] = []

    for page in book.get("pages", []):
        page_number = page.get("page_number")
        page_prompt = page.get("image_prompt_english", "")

        page_prompts.append(
            "Children's picture-book page illustration. "
            f"Style: {style}. "
            f"Scene for page {page_number}: {page_prompt}. "
            f"{shared_visual_style}"
        )

    return {
        "cover": cover_prompt,
        **{f"page_{i + 1}": prompt for i, prompt in enumerate(page_prompts)},
    }


def generate_book_images(book: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    prompts = build_image_prompts(book)

    cover_path = assets_dir / "cover.png"

    print("Generating cover image...")
    _generate_png(prompts["cover"], cover_path)

    book["cover_image"] = "assets/cover.png"

    for idx, page in enumerate(book.get("pages", []), start=1):
        print(f"Generating image for page {idx}...")

        img_path = assets_dir / f"page-{idx}.png"
        _generate_png(prompts[f"page_{idx}"], img_path)

        page["image"] = f"assets/page-{idx}.png"

    return book