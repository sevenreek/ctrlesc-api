import aiofiles
import os
import asyncio
from pathlib import Path

from settings import settings
from models.rooms import (
    RoomModelDetail,
    RoomModel,
)


async def fetch_file(file: str):
    async with aiofiles.open(file) as file:
        content = await file.read()
    return content


async def fetch_room_model_data(slug: str):
    return await fetch_file(
        os.path.join(settings.room_config_dir, os.path.basename(slug) + ".json")
    )


async def fetch_room_model_detail(slug: str):
    content = fetch_room_model_data(slug)
    return RoomModelDetail.model_validate_json(content)


async def fetch_room_models():
    model_files = os.listdir(settings.room_config_dir)
    jsons = await asyncio.gather(
        *(
            fetch_room_model_data(Path(file).stem)
            for file in model_files
            if file.endswith(".json")
        )
    )
    return [RoomModelDetail.model_validate_json(json) for json in jsons]
