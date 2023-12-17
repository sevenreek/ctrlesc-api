from typing import Literal
from fastapi import APIRouter, Request, HTTPException, status
import asyncio
from redis.asyncio import Redis
from escmodels.room import (
    RoomConfig,
    Room,
    RoomState,
    AnyRoomActionRequest,
    PuzzleSkipRequest,
)
from escmodels.puzzle import PuzzleType, make_puzzle, infer_puzzle_config
from escmodels.base import TimerState
from settings import settings
from lib.redis import DependsRedis
from lib.roomconfigs import fetch_room_configs, fetch_room_config
from sse_starlette import EventSourceResponse
import json
import nanoid

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
    update_type, room = topic_path[1:3]
    meta, data = {"room": room}, {}
    return_data = {"meta": meta, "data": data}
    event_data = json.loads(string_data)
    try:
        stage = topic_path[3]
        meta["stage"] = stage
    except IndexError:
        pass
    try:
        puzzle = topic_path[4]
        meta["puzzle"] = puzzle
    except IndexError:
        pass
    match update_type:
        case "state":
            data["state"] = event_data
        case "completion":
            data["completed"] = bool(event_data)
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


RoomAction = Literal["start", "stop", "pause", "add", "skip"]


@router.post("/{slug}/{action}", status_code=status.HTTP_200_OK)
async def details(
    slug: str,
    action: RoomAction,
    action_data: AnyRoomActionRequest,
    redis: DependsRedis,
):
    async with redis.pubsub() as ps:
        action_id = nanoid.generate()
        redis_ack_channel = f"room/ack/{slug}/{action_id}"
        await ps.subscribe(redis_ack_channel)
        request_data = {"action": action}
        if action == "skip":
            request_data.update(action_data.model_dump())
        elif action == "add":
            request_data.update(action_data.model_dump())
        await redis.publish(f"room/request/{slug}/{action_id}", action)
        message = await ps.get_message(ignore_subscribe_messages=True, timeout=3)
        await ps.unsubscribe(redis_ack_channel)
        if message is None:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail={
                    "message": f"Timed out waiting for response from {slug} for action {str(request_data)}."
                },
            )


@router.get("/puzzle/supported", response_model=list[PuzzleType])
async def get_supported_puzzles():
    return [t.value for t in PuzzleType]
