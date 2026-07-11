from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Rooms


async def get_all_rooms(session: AsyncSession) -> list[Rooms]:
    stmt = select(Rooms).order_by(Rooms.id)
    result = await session.scalars(stmt)
    return list(result.all())