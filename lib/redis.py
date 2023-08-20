from typing import Annotated, Any
from fastapi import Depends
import asyncio
import redis.asyncio as redis
from inspect import Signature

from lib.roomconfigs import fetch_room_models
from models.rooms import RoomModelDetail, RoomStateDetails, PuzzleState, StageState
from models.base import TimerState
from models.util import extract_model_default_fields
from settings import settings

global_client = redis.Redis(
    host=settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    port=settings.redis_port,
)


async def get_client():
    client = global_client.client()
    try:
        yield client
    finally:
        await client.close()


DependsRedis = Annotated[redis.Redis, Depends(get_client)]


def generate_room_initial_state(room: RoomModelDetail) -> dict[str, Any]:
    room_dict = room.model_dump(
        include={
            "slug": True,
            "stages": True,
        }
    )
    room_dict.update(extract_model_default_fields(RoomStateDetails))

    for stage in room_dict["stages"]:
        keys_present_in_state = StageState.model_fields.keys()
        keys_to_drop = stage.keys() - keys_present_in_state
        for key in keys_to_drop:
            stage.pop(key)
        for puzzle in stage["puzzles"]:
            puzzle.update(extract_model_default_fields(PuzzleState))
            puzzle["state"] = puzzle.pop("initial_state")
            keys_present_in_state = PuzzleState.model_fields.keys()
            keys_to_drop = puzzle.keys() - keys_present_in_state
            for key in keys_to_drop:
                puzzle.pop(key)

    return room_dict


def room_key(slug: str):
    return f"room:{slug}"


async def create_room_initial_states():
    rooms = await fetch_room_models()
    states = await asyncio.gather(
        *[global_client.json().get(room_key(room.slug)) for room in rooms]
    )
    empty_states = [
        slug
        for slug, state in zip((room.slug for room in rooms), states)
        if state is None
    ]
    await asyncio.gather(
        *[
            global_client.json().set(
                room_key(room_slug),
                "$",
                generate_room_initial_state(
                    next((r for r in rooms if r.slug == room_slug))
                ),
                True,
            )
            for room_slug in empty_states
        ]
    )


async def on_start():
    await create_room_initial_states()


async def on_exit():
    await global_client.close()