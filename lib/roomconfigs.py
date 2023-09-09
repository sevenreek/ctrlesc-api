import aiofiles
import os
import asyncio
from pathlib import Path
import json

from settings import settings
from models.rooms import (
    RoomModelDetail,
    RoomModelOverview,
)


async def fetch_file(file: str) -> str:
    async with aiofiles.open(file) as file:
        content = await file.read()
    return content


async def fetch_room_model_data(slug: str) -> str:
    return await fetch_file(
        os.path.join(settings.room_config_dir, os.path.basename(slug) + ".json")
    )


async def fetch_room_model_detail(slug: str):
    content = await fetch_room_model_data(slug)
    return RoomModelDetail.model_validate_json(content)


async def fetch_room_models() -> list[str]:
    model_files = os.listdir(settings.room_config_dir)
    files_data = await asyncio.gather(
        *(
            fetch_room_model_data(Path(file).stem)
            for file in model_files
            if file.endswith(".json")
        )
    )
    return files_data


def get_max_completion(room_dict):
    return sum(
        (
            puzzle["completion_worth"]
            for stage in room_dict["stages"]
            for puzzle in stage["puzzles"]
        )
    )


async def fetch_room_model_overviews():
    file_contents = await fetch_room_models()
    dicts = [json.loads(content) for content in file_contents]
    # Calculate max completion based on the configuration
    for room in dicts:
        room["max_completion"] = get_max_completion(room)
    return [RoomModelOverview.model_validate(json) for json in dicts]


async def fetch_room_model_details():
    jsons = await fetch_room_models()
    return [RoomModelDetail.model_validate_json(json) for json in jsons]
