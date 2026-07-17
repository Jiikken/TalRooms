from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.password import hash_password
from app.models.user import User, RoomsBooking


async def create_user(first_name: str, last_name: str, email: str, password: str, session: AsyncSession):
    """Создание нового пользователя"""
    hashed_password = hash_password(password)[:255]
    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        hashed_password=hashed_password
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def get_user_info(session: AsyncSession, email: str) -> dict | None:
    """Получение имени и фамилии пользователя"""
    stmt = (select(User.id, User.first_name, User.last_name, User.role, User.is_active, User.created, User.last_login)
            .where(User.email.ilike(email))
    )
    result = await session.execute(stmt)
    row = result.first()

    return {"id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "access_lvl": row[3],
            "is_active": row[4],
            "created": row[5],
            "last_login": row[6]
            } or None

async def get_user_by_id_bd(session: AsyncSession, user_id: int) -> dict | None:
    """Получение имени и фамилии пользователя"""
    stmt = (select(User).where(User.id == user_id))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return None

    return {"id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "access_lvl": user.role,
            "email": user.email,
            "is_active": user.is_active,
            "created": user.created,
            "last_login": user.last_login
            }

async def debug_user_exists(session: AsyncSession, email: str):
    stmt = (
        select(User.first_name)
        .where(User.email.ilike(email))
    )
    result = await session.execute(stmt)
    email_found = result.scalar_one_or_none()
    print(f"Email в БД: {email_found}")
    return email_found is not None

async def get_hashed_password(session: AsyncSession, email: str):
    """Достать хэшированный пароль"""
    result = await session.execute(
        select(User.hashed_password)
        .where(User.email.ilike(email))
    )
    row = result.first()
    if row:
        return row.hashed_password
    return None

async def update_user_activity(session: AsyncSession, email: str, last_login: str = None, is_active: Optional[bool] = None):
    """Обновление пользователя (время входа и активность)"""
    values = {}

    if is_active is not None:
        values["is_active"] = is_active

    if last_login is not None:
        values["last_login"] = last_login

    if not values:
        stmt = select(User.first_name, User.last_name).where(User.email.ilike(email))
        result = await session.execute(stmt)
        row = result.first()
        return {"first_name": row[0], "last_name": row[1]} if row else None

    stmt = (
        update(User)
        .where(User.email.ilike(email))
        .values(**values)
        .returning(User.id, User.first_name, User.last_name, User.is_active, User.last_login, User.role)
    )

    result = await session.execute(stmt)
    await session.commit()

    row = result.first()
    if row is None:
        return None

    return {
        "id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "is_active": row[3],
        "last_login": row[4],
        "access_lvl": row[5]
    }

async def is_room_available(session: AsyncSession, room_id: int, start: datetime, end: datetime) -> bool:
    """Свободна-ли комната"""
    stmt = select(RoomsBooking).where(
        RoomsBooking.room_id == room_id
    )
    result = await session.execute(stmt)
    return result.first() is None