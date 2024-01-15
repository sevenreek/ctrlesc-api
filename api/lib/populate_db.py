from api.lib.db import obtain_session
from escmodels.room import RoomConfig, StageConfig, AnyPuzzleConfig
from escmodels.db.models import Room, Stage, Puzzle
from sqlalchemy import delete


async def drop_all_room_configs():
    async with obtain_session() as session:
        await session.execute(delete(Puzzle))
        await session.execute(delete(Stage))
        await session.execute(delete(Room))
        await session.commit()


async def populate_db_room_configs(configs: list[RoomConfig]):
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

        await session.commit()
