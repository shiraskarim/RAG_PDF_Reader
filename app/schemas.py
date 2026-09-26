from pydantic import BaseModel, HttpUrl


class DocumentCreate(BaseModel):
    url: HttpUrl