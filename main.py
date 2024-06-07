"""App."""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import uvicorn

from constants import APP_HOST, APP_PORT

async def periodic_message():
    while True:
        print("Сообщение каждые 2 секунды")
        await asyncio.sleep(2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ background task starts at statrup """
    asyncio.create_task(periodic_message())
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)