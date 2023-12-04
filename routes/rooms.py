from fastapi import APIRouter, Request
import asyncio
from redis.asyncio import Redis
from models.room import RoomConfig, Room, RoomState
from models.puzzle import PuzzleType, make_puzzle, infer_puzzle_config
from models.base import TimerState
from settings import settings
from lib.redis import DependsRedis
from lib.roomconfigs import fetch_room_configs, fetch_room_config
from sse_starlette import EventSourceResponse
import json

router = APIRouter(prefix="/rooms", tags=["rooms"])


async def fetch_room_state_json(redis: Redis, slug: str):
    state = await redis.json().get(f"room:{slug}")
    return state


async def fetch_room_state(redis: Redis, slug: str):
    json = await fetch_room_state_json(redis, slug)
    return RoomState.model_validate(json)


@router.get("/", response_model=list[Room])
async def index(redis: DependsRedis):
    configs = await fetch_room_configs()
    slugs = (c.slug for c in configs)
    states = await asyncio.gather(
        *(fetch_room_state_json(redis, slug) for slug in slugs)
    )
    states = [RoomState.model_validate(state) for state in states]
    return [Room(config, state) for config, state in zip(configs, states)]


def create_sse_update(channel: str, string_data: str | None):
    topic_path = channel.split("/")
    update_type, room, stage = topic_path[1:4]
    return_data = {"room": room, "stage": stage}
    event_data = json.loads(string_data)
    try:
        puzzle = topic_path[4]
        return_data["puzzle"] = puzzle
    except IndexError:
        pass
    match update_type:
        case "state":
            return_data["state"] = event_data
        case "completion":
            return_data["completed"] = bool(event_data)
    return {"data": json.dumps(return_data), "event": "update"}


@router.get("/sse")
async def sse(request: Request, redis: DependsRedis):
    async def event_generator():
        async with redis.pubsub() as ps:
            await ps.psubscribe("room/state/*", "room/completion/*")
            while ps.subscribed:
                message = await ps.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    channel: str = message["channel"]
                    yield create_sse_update(channel, message.get("data", None))
                await asyncio.sleep(0.01)

    return EventSourceResponse(event_generator())


@router.get("/{slug}", response_model=Room)
async def details(slug: str, redis: DependsRedis):
    config, state = await asyncio.gather(
        fetch_room_config(slug), fetch_room_state(redis, slug)
    )
    return Room(config, state)


@router.get("/puzzle/supported", response_model=list[PuzzleType])
async def get_supported_puzzles():
    return [t.value for t in PuzzleType]
