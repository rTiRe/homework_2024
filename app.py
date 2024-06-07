"""App."""

from fastapi import FastAPI, Depends
from fastapi.routing import APIRouter
import asyncio

app = FastAPI()

async def periodic_message():
    while True:
        print("Сообщение каждые 2 секунды")
        await asyncio.sleep(2)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(periodic_message())


@app.get("/")
async def root():
    return {"message": "Hello World"}