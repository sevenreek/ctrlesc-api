from api.lib.db import obtain_session
from api.lib.mock.id import generate_snowflake_id
from escmodels.base.room import RoomConfig
from escmodels.db.models import Game, Room, Stage, Puzzle, StageCompletion, GameResult
from sqlalchemy import delete
import numpy as np
from random import randrange
from datetime import datetime, timedelta, time
from math import ceil, floor


async def drop_all_room_configs():
    async with obtain_session() as session:
        await session.execute(delete(Puzzle))
        await session.execute(delete(Stage))
        await session.execute(delete(Room))
        await session.commit()


async def populate_db_room_configs(configs: list[RoomConfig]) -> list[Room]:
    rooms: list[Room] = []
    async with obtain_session() as session:
        for room_config in configs:
            room = Room(**room_config.model_dump(exclude={"stages"}))
            for stage_index, stage_config in enumerate(room_config.stages):
                stage = Stage(
                    **stage_config.model_dump(exclude={"puzzles"}), index=stage_index
                )
                for puzzle_config in stage_config.puzzles:
                    puzzle = Puzzle(**puzzle_config.model_dump())
                    stage.puzzles.append(puzzle)
                room.stages.append(stage)
            session.add(room)
            rooms.append(room)

        await session.commit()
    return rooms


def get_stage_completion_value(stage: Stage):
    return sum(puzzle.completion_worth for puzzle in stage.puzzles)


def get_next_nice_datetime(
    dt: datetime,
    *,
    minute_granularity: int = 15,
    shift_start_time: time = time(12),
    shift_end_time: time = time(23),
):
    dt_time = dt.time()
    if dt_time > shift_end_time:
        return datetime(
            dt.year, dt.month, dt.day, shift_start_time.hour, shift_start_time.minute
        ) + timedelta(days=1)
    elif dt_time < shift_start_time:
        return datetime(
            dt.year, dt.month, dt.day, shift_start_time.hour, shift_start_time.second
        )
    minutes_in_day = dt.hour * 60 + dt.minute
    rounded_minutes = ceil(minutes_in_day / minute_granularity) * minute_granularity
    return datetime(dt.year, dt.month, dt.day) + timedelta(minutes=rounded_minutes)


async def populate_games(
    room: Room,
    *,
    game_count: int = 20,
    relative_time_variance: float = 0.15,
    time_per_completion_point: int = 60,
    throw_on_future: bool = True,
) -> list[Game]:
    games : list[Game] = []
    async with obtain_session() as session:
        now = datetime.now()
        next_timeslot = now - timedelta(
            days=randrange(floor(game_count * 0.5), game_count)
        )
        for game_index in range(game_count):
            game_datetime = get_next_nice_datetime(next_timeslot)
            if throw_on_future and game_datetime > now:
                raise ValueError(
                    f"Could not generate the requested {game_count} games. Gametime for game no. {game_index} would exceed current timestamp {now} at {game_datetime}."
                )
            game = Game(id= generate_snowflake_id(game_datetime, room.id) , room=room, started_on=game_datetime, created_on=game_datetime)
            total_seconds_taken: int = 0
            for stage in room.stages:
                stage_completion = get_stage_completion_value(stage)
                stage_time_mean = stage_completion * time_per_completion_point
                stage_time_variance = relative_time_variance * stage_time_mean
                final_stage_time = max(
                    30, int(np.random.normal(stage_time_mean, stage_time_variance))
                )
                total_seconds_taken += final_stage_time
                stage_completion = StageCompletion(
                    stage=stage,
                    game=game,
                    gametime=total_seconds_taken,
                    duration=final_stage_time,
                    created_on=game_datetime + timedelta(seconds=total_seconds_taken),
                )
                session.add(stage_completion)
            game.ended_on = game_datetime + timedelta(seconds=total_seconds_taken)
            game.result = GameResult.COMPLETED
            game.duration = total_seconds_taken
            next_timeslot = game_datetime + timedelta(
                seconds=room.base_time + 5 * 60
            )  # 5 min cleanup time
        session.add_all(games)
        await session.commit()
    return games
