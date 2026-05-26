from redis.asyncio import Redis
from gmail_webhook.gmail_watch import log


redis_client: Redis | None = None


async def init_redis():
    global redis_client

    redis_client = Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
    )

    try:
        await redis_client.ping()
        log.info("Redis connected")

    except Exception as exc:
        log.error("Redis connection failed: %s", exc)
        raise


async def close_redis():
    global redis_client

    if redis_client:
        await redis_client.close()
        log.info("Redis connection closed")