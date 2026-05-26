from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI

load_dotenv()

from gmail_webhook.routes import router as gmail_router
from slack_api.routes import router as slack_router
from contextlib import asynccontextmanager

from fastapi import FastAPI

from redis_client import (
    init_redis,
    close_redis,
)

# start and end with the fastapi server
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup
    await init_redis()

    yield

    # Shutdown
    await close_redis()


app = FastAPI(
    lifespan=lifespan,
)

app.include_router(gmail_router)
app.include_router(slack_router)

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0", port=8080)