from api.lib import erorrs
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast
from sqlalchemy.orm import joinedload
from escmodels.db.models import Game, StageCompletion, Stage, Room


async def fetch_stage_completions(db: AsyncSession, game_id: str):
    query = (
        select(StageCompletion)
        .join(Stage, Stage.id == StageCompletion.stage_id)
        .where(StageCompletion.game_id == game_id)
        .order_by(Stage.index)
    )
    result = await db.execute(query)
    return result.all()


async def fetch_game(db: AsyncSession, game_id: str):
    query = (
        select(Game)
        .where(Game.id == game_id)
        .options(joinedload(Game.stage_completions))
    )
    result = await db.execute(query)
    try:
        result = result.unique().scalar_one()
    except NoResultFound:
        raise erorrs.NotFound(f"The game {game_id} was not found")
    return result
