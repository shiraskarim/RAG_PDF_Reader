import asyncio
import json
import os

import aio_pika

from app.document_service import (
    download_pdf,
    update_document_status,
)
from app.database import AsyncSessionLocal
from app.chunker import create_chunks
from app.chunk_repository import save_chunks
from app.s3_service import upload_file

from app.pdf_processor import extract_pages
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"

QUEUE_NAME = "pdf_processing"

DOWNLOAD_DIR = "downloads"

MAX_RETRIES = 3


async def publish_to_retry(data: dict):

    connection = await aio_pika.connect_robust(
        RABBITMQ_URL
    )

    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "document_exchange",
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )

    await exchange.publish(
        aio_pika.Message(
            body=json.dumps(data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key="retry",
    )

    await connection.close()


async def publish_to_dlq(data: dict):

    connection = await aio_pika.connect_robust(
        RABBITMQ_URL
    )

    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "document_exchange",
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )

    await exchange.publish(
        aio_pika.Message(
            body=json.dumps(data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key="dead",
    )

    await connection.close()


async def process_message(message: aio_pika.IncomingMessage):

    data = json.loads(message.body.decode())

    document_id = data["document_id"]
    source_url = data["source_url"]

    attempt = data.get("attempt", 0)

    try:

        print(
            f"Processing {document_id}, "
            f"attempt={attempt}"
        )

        await update_document_status(
            document_id,
            "PROCESSING",
            processing_stage="DOWNLOADING",
        )

        os.makedirs(
            DOWNLOAD_DIR,
            exist_ok=True,
        )

        file_path = os.path.join(
            DOWNLOAD_DIR,
            f"{document_id}.pdf",
        )

        # -------------------------
        # Download PDF
        # -------------------------

        await download_pdf(
            source_url,
            file_path,
        )

        print(
            f"PDF downloaded: {document_id}"
        )

        # -------------------------
        # Upload to S3
        # -------------------------
        await update_document_status(
            document_id,
            "PROCESSING",
            processing_stage="UPLOADING",
        )
        s3_key = f"documents/{document_id}.pdf"

        s3_location = await upload_file(
            file_path,
            s3_key,
        )
        print(
                    f"Uploaded to S3: {s3_location}"
                )
               
        await update_document_status(
            document_id,
            "PROCESSING",
            s3_location=s3_location,
            processing_stage="EXTRACTING",
        )
        pages = extract_pages(file_path)

        await update_document_status(
            document_id,
            "PROCESSING",
            s3_location=s3_location,
            processing_stage="CHUNKING",
        )
        chunks = create_chunks(document_id, pages)

        await update_document_status(
            document_id,
            "PROCESSING",
            s3_location=s3_location,
            processing_stage="SAVING_CHUNKS",
        )
        async with AsyncSessionLocal() as db:
            await save_chunks(db, chunks)
       
        # -------------------------
        # Update DB
        # -------------------------

        await update_document_status(
            document_id,
            "COMPLETED",
            s3_location=s3_location,
            error=None,
            processing_stage="COMPLETED",
        )

        # -------------------------
        # ACK
        # -------------------------

        await message.ack()

        print(
            f"SUCCESS: {document_id}"
        )

    except Exception as e:

        print(
            f"FAILED: {document_id} "
            f"error={e}"
        )

        attempt += 1

        # -------------------------
        # Maximum retries reached
        # -------------------------

        if attempt > MAX_RETRIES:

            await update_document_status(
                document_id,
                "FAILED",
                error=str(e),
            )

            dlq_data = {
                "document_id": document_id,
                "source_url": source_url,
                "attempt": attempt,
                "error": str(e),
            }

            await publish_to_dlq(
                dlq_data
            )

            await message.ack()

            print(
                f"DLQ: {document_id}"
            )

            return

        # -------------------------
        # Retry
        # -------------------------

        retry_data = {
            "document_id": document_id,
            "source_url": source_url,
            "attempt": attempt,
        }

        await publish_to_retry(
            retry_data
        )

        await message.ack()

        print(
            f"RETRY: {document_id} "
            f"attempt={attempt}"
        )


async def main():

    connection = await aio_pika.connect_robust(
        RABBITMQ_URL
    )

    channel = await connection.channel()

    await channel.set_qos(
        prefetch_count=1
    )

    queue = await channel.declare_queue(
        QUEUE_NAME,
        durable=True,
    )

    print("PDF worker started...")
    print("Waiting for messages...")

    await queue.consume(
        process_message
    )

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
