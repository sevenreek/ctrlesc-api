from fastapi import FastAPI
from contextlib import asynccontextmanager
from lib.redis import on_exit as redis_exit, on_start as redis_start
from lib.mqtt import on_exit as mqtt_exit, on_start as mqtt_start

from routes.rooms import router as room_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_start()
    await mqtt_start()
    yield
    await redis_exit()
    await mqtt_exit()


app = FastAPI(lifespan=lifespan)

app.include_router(room_router)


@app.get("/")
async def index():
    return "Hello world!"
