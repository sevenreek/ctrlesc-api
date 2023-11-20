from fastapi import APIRouter, Request
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
from models.rooms.components import UIComponentType
from models.base import TimerState
from settings import settings
from lib.redis import DependsRedis
from lib.roomconfigs import fetch_room_model_overviews, fetch_room_model_detail
from sse_starlette import EventSourceResponse
import json

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


@router.get("/sse")
async def sse(request: Request, redis: DependsRedis):
    async def event_generator():
        async with redis.pubsub() as ps:
            await ps.psubscribe("room/state/*")
            while ps.subscribed:
                message = await ps.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    channel: str = message["channel"]
                    puzzle_topic_path = channel.split("/")
                    room, stage, puzzle = puzzle_topic_path[-3:]
                    state = json.loads(message["data"])
                    yield json.dumps(
                        {"room": room, "stage": stage, "puzzle": puzzle, "state": state}
                    )
                await asyncio.sleep(0.01)

    return EventSourceResponse(event_generator())


@router.get("/{slug}", response_model=RoomDetail)
async def details(slug: str, redis: DependsRedis):
    model, state = await asyncio.gather(
        fetch_room_model_detail(slug), fetch_room_state_detail(redis, slug)
    )
    return RoomDetail(model, state)


@router.get("/components/supported", response_model=list[UIComponentType])
async def get_supported_component_types():
    return [t.value for t in UIComponentType]
