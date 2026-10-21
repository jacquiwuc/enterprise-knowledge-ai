
from pydantic import BaseModel, Field, HttpUrl


class TextChunk(BaseModel):
    chunk_id: str = Field(min_length=1)
    source_url: HttpUrl
    title: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)
    text: str = Field(min_length=1)
