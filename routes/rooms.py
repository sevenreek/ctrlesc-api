from fastapi import APIRouter
import asyncio
from redis.asyncio import Redis

from models.rooms import (
    RoomDetails,
    RoomOverview,
    Stage,
    Puzzle,
    RoomModelDetail,
    RoomModel,
    RoomStateDetails,
    RoomStateOverview,
)
from models.base import TimerState
from settings import settings
from lib.redis import DependsRedis
from lib.roomconfigs import fetch_room_models


router = APIRouter(prefix="/rooms", tags=["rooms"])


def get_room_state_redis_key(slug: str):
    return "room." + slug + ".state"


async def fetch_room_state(redis: Redis, slug: str):
    key = get_room_state_redis_key(slug)
    state = await redis.hgetall(key)
    return state


@router.get("/", response_model=list[RoomOverview])
async def index(redis: DependsRedis):
    models = await fetch_room_models()
    slugs = (m.slug for m in models)
    states = await asyncio.gather(*(fetch_room_state(redis, slug) for slug in slugs))
    states = [RoomStateOverview.model_validate(state) for state in states]
    return [
        RoomOverview(**m.model_dump(), **s.model_dump()) for m, s in zip(models, states)
    ]
