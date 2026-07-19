from datetime import datetime

from sqlalchemy import select, or_, exists, update, delete
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

async def get_room_by_id(session: AsyncSession, room_id):
    """Получение ID комнаты по имени"""
    stmt = (
        select(Rooms)
        .where(Rooms.id == room_id)
    )
    result = await session.execute(stmt)
    room = result.scalars().all()
    return room

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

async def delete_booked_room(session: AsyncSession, room_id: int, date: datetime) -> bool:
    """Удаление забронированной комнаты"""
    print(date)
    stmt = (
        delete(RoomsBooking)
        .where(RoomsBooking.room_id == room_id, RoomsBooking.date == date)
        .execution_options(synchronize_session=False)
    )
    result = await session.execute(stmt)
    await session.commit()

    return result.rowcount > 0

async def get_booked_room_by_room_id_and_date(session: AsyncSession, room_id: int, date: datetime):
    """Получение забронированной комнаты по её ID и дате бронирования"""
    stmt = (
        select(RoomsBooking)
        .where(RoomsBooking.room_id == room_id, RoomsBooking.date == date)
        .options(selectinload(RoomsBooking.room))
    )
    result = await session.execute(stmt)
    room = result.scalar_one_or_none()

    if room is None:
        return None

    return {
        "id": room.id,
        "room_id": room.room_id,
        "booked_by_id": room.booked_by_id,
        "requested_by_id": room.requested_by_id,
        "date": room.date,
        "create_at": room.created_at,
        "room": room.room
    }

async def update_booked_room(session: AsyncSession, room_id: int, date: datetime, new_room_id: int, new_date: datetime):
    """Обновление данных забронированной комнаты"""
    stmt = (
        update(RoomsBooking)
        .where(RoomsBooking.room_id == room_id, RoomsBooking.date == date)
        .values(room_id=new_room_id, date=new_date)
    )
    await session.execute(stmt)
    await session.commit()

async def get_all_booked_rooms(session: AsyncSession) -> list[RoomsBooking]:
    """Получение всех забронированных комнат"""
    stmt = (
        select(RoomsBooking)
        .order_by(RoomsBooking.id)
    )
    result = await session.scalars(stmt)
    return list(result.all())
