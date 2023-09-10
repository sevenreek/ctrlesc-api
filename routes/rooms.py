from fastapi import APIRouter
import asyncio
from redis.asyncio import Redis

from models.rooms import (
    RoomModelOverview,
    RoomModelDetail,
    RoomStateDetail,
    RoomStateOverview,
    RoomDetail,
    RoomOverview,
)
from models.base import TimerState
from settings import settings
from lib.redis import DependsRedis
from lib.roomconfigs import fetch_room_model_overviews, fetch_room_model_detail


router = APIRouter(prefix="/rooms", tags=["rooms"])


async def fetch_room_state_json(redis: Redis, slug: str):
    state = await redis.json().get(f"room:{slug}")
    return state


async def fetch_room_state_detail(redis: Redis, slug: str):
    json = await fetch_room_state_json(redis, slug)
    return RoomStateDetail.model_validate(json)


@router.get("/", response_model=list[RoomOverview])
async def index(redis: DependsRedis):
    models = await fetch_room_model_overviews()
    slugs = (m.slug for m in models)
    states = await asyncio.gather(
        *(fetch_room_state_json(redis, slug) for slug in slugs)
    )
    states = [RoomStateOverview.model_validate(state) for state in states]
    return [
        RoomOverview(**(model.model_dump() | state.model_dump()))
        for model, state in zip(models, states)
    ]


@router.get("/{slug}", response_model=RoomDetail)
async def details(slug: str, redis: DependsRedis):
    model, state = await asyncio.gather(
        fetch_room_model_detail(slug), fetch_room_state_detail(redis, slug)
    )
    return RoomDetail(model, state)


from models.rooms.components import ComponentUnion


@router.get("/test", response_model=ComponentUnion)
async def test(slug: str, redis: DependsRedis):
    return None
