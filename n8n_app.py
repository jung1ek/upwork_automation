from dotenv import load_dotenv

load_dotenv()

from contextlib import asynccontextmanager

from fastapi import FastAPI
from n8n_endpoints import router as get_job_router
from slack_api.routes import router as slack_router
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

app.include_router(get_job_router)
app.include_router(slack_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)