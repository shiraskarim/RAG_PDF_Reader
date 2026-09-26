# app/chunk_repository.py

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DocumentChunk
from app.chunker import Chunk


async def save_chunks(
    db: AsyncSession,
    chunks: list[Chunk],
):
    if not chunks:
        return

    values = [
        {
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "page_start": chunk.page_start,
            "page_end": chunk.page_end,
            "text": chunk.text,
            "token_count": len(chunk.text.split()),
        }
        for chunk in chunks
    ]

    stmt = insert(DocumentChunk).values(values)

    stmt = stmt.on_conflict_do_nothing(
        constraint="uq_document_chunk"
    )

    await db.execute(stmt)
    await db.commit()