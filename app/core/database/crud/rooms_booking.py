from datetime import datetime

from sqlalchemy import select, or_, exists, update, join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import RoomsBooking, Rooms


async def get_user_booking(session: AsyncSession, user_id: int):
    """Получение броней пользователя"""
    stmt = (select(RoomsBooking)
            .join(Rooms, RoomsBooking.room_id == Rooms.id)
            .where(or_(RoomsBooking.booked_by_id == user_id, RoomsBooking.requested_by_id == user_id))
            .options(selectinload(RoomsBooking.room))
            .order_by(Rooms.start_time.desc())
    )

    result = await session.execute(stmt)
    booking = result.scalars().all()
    return booking


async def is_room_available_exists(
        session: AsyncSession,
        room_id: int,
        date: datetime) -> bool:
    stmt = select(
        exists().where(
            RoomsBooking.room_id == room_id,
            RoomsBooking.date == date
        )
    )
    result = await session.execute(stmt)
    exists_flag = result.scalar()
    return not exists_flag

async def update_status_room(session: AsyncSession, room_id, new_status):
    """Изменение статуса комнаты"""
    stmt = (
        update(Rooms)
        .where(Rooms.id == room_id)
        .values(status=new_status)
    )
    await session.execute(stmt)
    await session.commit()

async def create_booking(session: AsyncSession,
                         room_id: int,
                         employee_id: int,
                         client_id: int,
                         date: datetime) -> RoomsBooking:
    """Создание объекта арендованной комнаты"""
    if not await is_room_available_exists(session, room_id, date):
        raise ValueError("Комната уже забронирована на это время")

    booking = RoomsBooking(room_id=room_id, booked_by_id=employee_id, requested_by_id=client_id, date=date)

    session.add(booking)
    await session.commit()
    await session.refresh(booking)

    return booking