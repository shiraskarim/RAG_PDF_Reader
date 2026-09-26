# app/chunker.py

from dataclasses import dataclass

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)


@dataclass
class Chunk:
    document_id: str
    chunk_index: int
    page_start: int
    page_end: int
    text: str


splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=300,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        "",
    ],
)


def create_chunks(
    document_id: str,
    pages: list[dict],
) -> list[Chunk]:

    chunks = []
    chunk_index = 0

    for page in pages:

        page_number = page["page_number"]
        text = page["text"]

        if not text.strip():
            continue

        page_chunks = splitter.split_text(text)

        for chunk_text in page_chunks:

            chunks.append(
                Chunk(
                    document_id=document_id,
                    chunk_index=chunk_index,
                    page_start=page_number,
                    page_end=page_number,
                    text=chunk_text,
                )
            )

            chunk_index += 1

    return chunks