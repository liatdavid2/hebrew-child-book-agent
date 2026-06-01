import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv

load_dotenv()

ENABLE_NIKUD = os.getenv("ENABLE_NIKUD", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def diacritize_text(text: str) -> str:
    if not ENABLE_NIKUD:
        return text

    if not text or not text.strip():
        return text

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_path = tmp_path / "input.txt"
        output_path = tmp_path / "output.txt"

        input_path.write_text(text, encoding="utf-8")

        try:
            subprocess.run(
                [
                    "diacritize",
                    str(input_path),
                    f"-o={output_path}",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "Nakdimon was not found. Run: pip install nakdimon"
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"Nakdimon failed: {exc.stderr or exc.stdout}"
            ) from exc

        return output_path.read_text(encoding="utf-8").strip()


def add_nikud_to_book(book: Dict[str, Any]) -> Dict[str, Any]:
    if not ENABLE_NIKUD:
        return book

    book["cover_text"] = diacritize_text(book.get("cover_text", ""))

    for page in book.get("pages", []):
        page["final_text"] = diacritize_text(page.get("final_text", ""))

    return book