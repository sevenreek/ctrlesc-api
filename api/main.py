from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.lib.redis import on_exit as redis_exit, on_start as redis_start
from api.lib.mqtt import on_exit as mqtt_exit, on_start as mqtt_start
from api.lib.mock.db import (
    populate_db_room_configs,
    drop_all_room_configs,
    populate_games,
)
from escmodels.db.models import *
from api.lib.roomconfigs import fetch_room_configs

from api.routes.rooms import router as room_router


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
