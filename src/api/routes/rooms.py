from typing import Literal, Annotated, Any
from collections.abc import Iterable
import time

from api.lib.db import DependsDB
from fastapi import APIRouter, Request, HTTPException, status, Query
import asyncio
import humps
from redis.asyncio import Redis
from api.lib.db.games import fetch_game
import escmodels.base as base
import escmodels.db as dbm
import escmodels.api.out as out
from escmodels.requests import AnyRoomActionRequest, RequestResult
from api.lib.redis import DependsRedis
from api.lib.roomconfigs import fetch_room_configs, fetch_room_config
from sse_starlette import EventSourceResponse
import json
import nanoid
from sqlalchemy import select, func
import sqlalchemy as sa

router = APIRouter(prefix="/rooms", tags=["rooms"])


async def fetch_room_state_json(redis: Redis, slug: str):
    state = await redis.json().get(f"room:{slug}")
    return state


async def fetch_room_state(redis: Redis, slug: str):
    json = await fetch_room_state_json(redis, slug)
    return base.RoomState.model_validate(json)


@router.get("", response_model=list[out.Room])
async def index(redis: DependsRedis):
    configs = await fetch_room_configs()
    slugs = (c.slug for c in configs)
    states = await asyncio.gather(
        *(fetch_room_state_json(redis, slug) for slug in slugs)
    )
    states = [base.RoomState.model_validate(state) for state in states]
    return [out.Room.create(config, state) for config, state in zip(configs, states)]


def create_sse_update(channel: str, string_data: str | None):
    topic_path = channel.split("/")
    update_type, room = topic_path[1:3]
    update_data: dict[str, Any]= {}
    return_data = {"room": room, "update": update_data}
    event_data: dict[str, Any] | bool | None = None if string_data is None else json.loads(string_data)
    try:
        stage = topic_path[3]
        return_data["stage"] = stage
        puzzle = topic_path[4]
        return_data["puzzle"] = puzzle
    except IndexError:
        pass
    match update_type:
        case "state":
            if not isinstance(event_data, dict): raise TypeError(f"state update event data is not a dict but {type(event_data)}")
            update_data.update(
                {humps.camelize(key): value for key, value in event_data.items()}
            )
        case "completion":
            update_data["completed"] = bool(event_data)
        case _:
            raise RuntimeError(f"unknown update type {update_type}")
    return {"data": json.dumps(return_data), "event": "update"}


@router.get("/sse")
async def sse(request: Request, redis: DependsRedis):
    async def event_generator():
        async with redis.pubsub() as ps:
            await ps.psubscribe("room/state/*", "room/completion/*")
            while ps.subscribed:
                message = await ps.get_message(
                    ignore_subscribe_messages=True
                )
                if message is not None:
                    channel: str = message["channel"]
                    yield create_sse_update(channel, message.get("data", None))  # pyright: ignore[reportArgumentType]
                await asyncio.sleep(0.01)

    return EventSourceResponse(event_generator())


@router.get("/{slug}", response_model=out.RoomGame)
async def room_details(redis: DependsRedis, db: DependsDB, slug: str):
    config, state = await asyncio.gather(
        fetch_room_config(slug), fetch_room_state(redis, slug)
    )
    if state.active_game_id is None:
        game = None
    else:
        db_game = await fetch_game(db, state.active_game_id)
        game = out.Game.from_db(db_game)
    return out.RoomGame.create(config, state, game)


@router.get("/{slug}/config", response_model=out.RoomConfig)
async def room_config(slug: str, redis: DependsRedis):
    config = await fetch_room_config(slug)
    return out.RoomConfig.model_validate(config)


AllowedCompletions = Literal[
    "best",
    "worst",
    "average",
]
AllowedCompletionsQueryType = Annotated[Iterable[AllowedCompletions], Query()]

FUNC_MAPPING = {
    "best": func.min,
    "worst": func.max,
    "average": func.avg,
}


@router.get("/{slug}/segments")
async def segments(
    db: DependsDB,
    slug: str,
    funcs: AllowedCompletionsQueryType = AllowedCompletions.__args__,
):
    select_keys = [
        sa.cast(
            FUNC_MAPPING[label](dbm.StageCompletion.duration).label(label),
            sa.Double,
        )
        for label in funcs
    ]
    query = (
        select(*select_keys)
        .join(dbm.Stage, dbm.Stage.id == dbm.StageCompletion.stage_id)
        .join(dbm.Room, dbm.Room.id == dbm.Stage.room_id)
        .where(dbm.Room.slug == slug)
        .group_by(dbm.Stage.index)
        .order_by(dbm.Stage.index)
    )
    result = await db.execute(query)
    rows = result.all()
    return {key: [row._mapping[key] for row in rows] for key in funcs}


@router.post(
    "/{slug}/request", status_code=status.HTTP_200_OK, response_model=RequestResult
)
async def request(redis: DependsRedis, slug: str, action_data: AnyRoomActionRequest):
    async with redis.pubsub() as ps:
        action_id = nanoid.generate()
        redis_ack_channel = f"room/ack/{slug}/{action_id}"
        await ps.subscribe(redis_ack_channel)
        request_data = action_data.model_dump()
        if action_data.action == "skip":
            request_data.update(action_data.model_dump())
        elif action_data.action == "add":
            request_data.update(action_data.model_dump())
        await redis.publish(
            f"room/request/{slug}/{action_id}", json.dumps(request_data)
        )
        timeout_start = time.time()
        message = None
        while time.time() < timeout_start + 3 and message is None:
            message = await ps.get_message(ignore_subscribe_messages=True)
            await asyncio.sleep(0.05)
        await ps.unsubscribe(redis_ack_channel)
        if message is None:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail={
                    "message": f"Timed out waiting for response from {slug} for action {str(request_data)}."
                },
            )
        return RequestResult.model_validate_json(message["data"])


@router.get("/{slug}/games/{game_id}")
async def game(slug: str, game_id: str, db: DependsDB):
    result = await fetch_game(db, game_id)
    return result


@router.get("/puzzle/supported", response_model=list[base.PuzzleType])
async def get_supported_puzzles():
    return [t.value for t in base.PuzzleType]
