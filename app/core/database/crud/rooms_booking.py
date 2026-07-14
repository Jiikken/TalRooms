from datetime import datetime

from sqlalchemy import select, or_, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RoomsBooking

async def get_user_booking(session: AsyncSession, user_id: int):
    """Получение броней пользователя"""
    stmt = (select(RoomsBooking)
            .where(or_(RoomsBooking.booked_by_id == user_id, RoomsBooking.requested_by_id == user_id))
            .order_by(RoomsBooking.start_time.desc())
    )

    result = await session.execute(stmt)
    return result.scalars().all()


async def is_room_available_exists(
        session: AsyncSession,
        room_id: int,
        date: datetime,
        start_time: datetime,
        end_time: datetime) -> bool:
    stmt = select(
        exists().where(
            RoomsBooking.room_id == room_id,
            RoomsBooking.date == date,
            RoomsBooking.start_time < end_time,
            RoomsBooking.end_time > start_time
        )
    )
    result = await session.execute(stmt)
    exists_flag = result.scalar()
    return not exists_flag

async def create_booking(session: AsyncSession,
                         room_id: int,
                         employee_id: int,
                         client_id: int,
                         date: datetime,
                         start_time: datetime,
                         end_time: datetime) -> RoomsBooking:
    """Создание объекта арендованной комнаты"""
    if not await is_room_available_exists(session, room_id, date, start_time, end_time):
        raise ValueError("Комната уже забронирована на это время")

    booking = RoomsBooking(room_id=room_id, booked_by_id=employee_id, requested_by_id=client_id, date=date, start_time=start_time, end_time=end_time)

    session.add(booking)
    await session.commit()
    await session.refresh(booking)

    return booking