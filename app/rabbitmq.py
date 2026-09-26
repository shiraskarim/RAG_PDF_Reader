import json
import aio_pika


RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
async def setup_exchange(channel):

    exchange = await channel.declare_exchange(
        "document_exchange",
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )

    main_queue = await channel.declare_queue(
        "pdf_processing",
        durable=True,
    )

    retry_queue = await channel.declare_queue(
    "pdf_retry",
    durable=True,
    arguments={
        "x-message-ttl": 5000,
        "x-dead-letter-exchange": "document_exchange",
        "x-dead-letter-routing-key": "process",
    },
)

    dlq = await channel.declare_queue(
        "pdf_processing_dlq",
        durable=True,
    )

    await main_queue.bind(
        exchange,
        routing_key="process",
    )

    await retry_queue.bind(
        exchange,
        routing_key="retry",
    )

    await dlq.bind(
        exchange,
        routing_key="dead",
    )

    return exchange

async def get_connection():
    connection = await aio_pika.connect_robust(
        RABBITMQ_URL
    )

    return connection


async def publish_document( document_id: str,
    source_url: str):

    connection = await get_connection()

    channel = await connection.channel()

    exchange = await setup_exchange(channel)

    message = {
        "document_id": document_id,
        "source_url": str(source_url),
        "attempt": 0,
    }

    await exchange.publish(
        aio_pika.Message(
            body=json.dumps(message).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key="process",
    )

    await connection.close()