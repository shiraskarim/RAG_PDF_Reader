import os
import uuid
import tempfile
from app.rabbitmq import publish_document
from fastapi import FastAPI,Depends
from app.database import Base, engine, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Document
from app.database import init_db
from app.schemas import DocumentCreate
from app.document_service import download_pdf
from app.s3_service import upload_file
from contextlib import asynccontextmanager

# Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
@app.post("/documents")
async def create_document(request: DocumentCreate,db: AsyncSession = Depends(get_db)):
    
    document_id = str(uuid.uuid4())

    document = Document(
        document_id=document_id,
        source_url=str(request.url),
        status="WAITING",
        processing_stage="QUEUED",
    )

    db.add(document)

    await db.commit()

    await publish_document(
        document_id=document_id,
        source_url=str(request.url),
    )

    return {
        "document_id": document_id,
        "status": "WAITING",
    }