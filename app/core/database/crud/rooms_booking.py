from datetime import datetime

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RoomsBooking


async def create_booking(session: AsyncSession, room_id: int, employee_id: int, client_id: int, date: datetime, start_time: datetime, end_time: datetime) -> RoomsBooking:
    """Создание объекта арендованной комнаты"""
    booking = RoomsBooking(room_id=room_id, booked_by_id=employee_id, requested_by_id=client_id, date=date, start_time=start_time, end_time=end_time)

    session.add(booking)
    await session.commit()
    await session.refresh(booking)

    return booking

async def get_user_booking(session: AsyncSession, user_id: int):
    """Получение броней пользователя"""
    stmt = (select(RoomsBooking)
            .where(or_(RoomsBooking.booked_by_id == user_id, RoomsBooking.requested_by_id == user_id))
            .order_by(RoomsBooking.start_time.desc())
    )

    result = await session.execute(stmt)
    return result.scalars().all()