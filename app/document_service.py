import httpx

from sqlalchemy import update

from app.database import AsyncSessionLocal
from app.models import Document
async def download_pdf(url: str, output_path: str):

    async with httpx.AsyncClient() as client:

        response = await client.get(
            url,
            timeout=30
        )

        response.raise_for_status()

        with open(output_path, "wb") as file:
            file.write(response.content)

    return output_path




async def update_document_status(
    document_id: str,
    status: str,
    s3_location: str | None = None,
    error: str | None = None,
    processing_stage: str | None = None,
):

    async with AsyncSessionLocal() as session:

        stmt = (
            update(Document)
            .where(Document.document_id == document_id)
            .values(
                status=status,
                s3_location=s3_location,
                error=error,
                processing_stage=processing_stage,
            )
        )

        await session.execute(stmt)

        await session.commit()

# async def download_pdf(url: str, output_path: str):

#     async with httpx.AsyncClient() as client:

#         async with client.stream(
#             "GET",
#             url,
#             timeout=60
#         ) as response:

#             response.raise_for_status()

#             with open(output_path, "wb+") as file:

#                 async for chunk in response.aiter_bytes(
#                     chunk_size=1024 * 1024
#                 ):
#                     file.write(chunk)

#     return output_path