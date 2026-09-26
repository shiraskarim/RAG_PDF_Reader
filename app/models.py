from datetime import datetime,timezone

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,func,UniqueConstraint,ForeignKey,
    Text,
)
from sqlalchemy.orm import declarative_base
from app.database import Base
class DocumentChunk(Base):
    
    __tablename__ = "document_chunks"

    id = Column(
        Integer,
        primary_key=True,
    )

    document_id = Column(
        String,
        ForeignKey("documents.document_id"),
        nullable=False,
    )

    chunk_index = Column(
        Integer,
        nullable=False,
    )

    page_start = Column(
        Integer,
        nullable=False,
    )

    page_end = Column(
        Integer,
        nullable=False,
    )

    text = Column(
        Text,
        nullable=False,
    )

    token_count = Column(
        Integer,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunk",
        ),
    )

class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    document_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    source_url = Column(
        Text,
        nullable=False
    )

    s3_location = Column(
        Text,
        nullable=True
    )

    status = Column(
        String,
        nullable=False
    )

    error = Column(
        Text,
        nullable=True
    )
    processing_stage = Column(
        String,
        nullable=True,
    )


    created_at = Column(
    DateTime(timezone=True), 
    server_default=func.now()
)

    updated_at = Column(
    DateTime(timezone=True), 
    server_default=func.now(), 
    onupdate=func.now()
)