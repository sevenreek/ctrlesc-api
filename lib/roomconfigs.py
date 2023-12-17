import aiofiles
import os
import asyncio
from pathlib import Path
import json

from settings import settings
from escmodels.room import RoomConfig


async def fetch_file(file: str) -> str:
    """Returns the content of a file. Unsafe.

    Args:
        file (str): Filepath.

    Returns:
        str: File content.
    """
    async with aiofiles.open(file) as file:
        content = await file.read()
    return content


async def fetch_room_config_data(slug: str) -> str:
    """Fetches a room config based on the provided slug. Unsafe.
    TODO: Make this safe.

    Args:
        slug (str): Room slug.

    Returns:
        str: Configuration in unparsed JSON.
    """
    return await fetch_file(
        os.path.join(settings.room_config_dir, os.path.basename(slug) + ".json")
    )


async def fetch_room_config(slug: str):
    """Fetches a parsed room config based on the provided slug.

    Args:
        slug (str): Room slug.

    Returns:
        RoomConfig: A parsed config for the room.
    """
    content = await fetch_room_config_data(slug)
    return RoomConfig.model_validate_json(content)


async def fetch_room_configs_data() -> list[str]:
    """Fetches unparsed configs for all of the available rooms.

    Returns:
        list[str]: List of unparsed config contents.
    """
    model_files = os.listdir(settings.room_config_dir)
    files_data = await asyncio.gather(
        *(
            fetch_room_config_data(Path(file).stem)
            for file in model_files
            if file.endswith(".json")
        )
    )
    return files_data


async def fetch_room_configs():
    """Fetches and parses room configurations for the available rooms.

    Returns:
        list[RoomConfig]: A list of room configurations.
    """
    file_contents = await fetch_room_configs_data()
    return [RoomConfig.model_validate_json(json) for json in file_contents]
