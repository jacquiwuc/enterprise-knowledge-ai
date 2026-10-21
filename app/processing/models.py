from pydantic import BaseModel, Field, HttpUrl


class Document(BaseModel):
    source_url: HttpUrl
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    content_hash: str = Field(min_length=64, max_length=64)
