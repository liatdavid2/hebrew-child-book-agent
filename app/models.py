from typing import List, Optional
from pydantic import BaseModel, Field


class PageInput(BaseModel):
    page_number: int = Field(..., ge=1)
    text: str = Field(..., min_length=1)


class BookRequest(BaseModel):
    cover_text: str = Field(..., min_length=1)
    child_age: Optional[str] = "4-7"
    style_instructions: Optional[str] = ""
    pages: List[PageInput] = Field(..., min_length=1)
