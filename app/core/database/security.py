from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def exists_user(session: AsyncSession, email: str) -> bool:
    """Проверка на существование пользователя"""
    query = select(exists().where(User.email == email))
    result = await session.execute(query)
    return result.scalar()