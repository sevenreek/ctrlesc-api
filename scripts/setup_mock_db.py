from api.lib.db import recreate_schema
from api.lib.mock.db import (
    drop_all_room_configs,
    populate_db_room_configs,
    populate_games,
)
from api.lib.roomconfigs import fetch_room_configs
import asyncio


async def setup_mock_db():
    await recreate_schema()
    await drop_all_room_configs()
    configs = await fetch_room_configs()
    db_configs = await populate_db_room_configs(configs)
    for roomconfig in db_configs:
        _ = await populate_games(roomconfig)


def sync_setup_mock_db():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_mock_db())


if __name__ == "__main__":
    sync_setup_mock_db()
