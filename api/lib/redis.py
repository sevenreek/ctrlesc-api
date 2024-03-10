from typing import Annotated
from fastapi import Depends
import asyncio
import redis.asyncio as redis
from api.lib.roomconfigs import fetch_room_configs
import escmodels.base as base
from escmodels.base.room import generate_room_initial_state
from api.settings import settings

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


def room_key(slug: str):
    return f"room:{slug}"


async def create_room_initial_states():
    rooms = await fetch_room_configs()
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
