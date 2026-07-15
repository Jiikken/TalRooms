from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.params import Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.connect import get_db
from app.core.database.crud.rooms import get_all_rooms
from app.core.database.crud.rooms_booking import create_booking, get_user_booking, get_booked_room_by_id
from app.core.security.JWT import get_info_from_access_token

router = APIRouter(prefix="/booking-rooms")

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "frontend" / "templates")

@router.get("/")
async def rooms(request: Request):
    """Все доступные комнаты для бронирования"""
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")

    room_id = request.cookies.get("room_id")

    today_date = datetime.now().strftime("%d.%m.%Y")

    return templates.TemplateResponse(request, "booking_rooms.html", {"room_id": room_id, "today_date": today_date})

@router.post("/room-id")
async def rooms(request: Request, response: Response):
    """Получение roomId"""
    data = await request.json()
    room_id = data.get("room_id")

    response.set_cookie(key="room_id", value=room_id, httponly=True)
    return room_id

@router.get("/get-all-rooms")
async def all_rooms(session: AsyncSession = Depends(get_db)):
    """Возвращает список всех комнат"""
    rooms_list = await get_all_rooms(session)
    return {"rooms": rooms_list}

@router.post("/book-room")
async def book_room(request: Request, session: AsyncSession = Depends(get_db)):
    """Получение данных аренды комнаты"""
    data = await request.json()
    employee_id = int(data.get("employeeId"))
    client_id = int(data.get("clientId"))
    room_id = int(data.get("roomId"))
    date = datetime.strptime(data.get("date"), "%Y-%m-%d")

    try:
        booking_room = await create_booking(session, room_id, employee_id, client_id, date)
    except ValueError:
        return {"booking": "null"}

    return {"booking": booking_room}

@router.get("/get/booked-room/{room_id}")
async def get_info_booked_room_by_id(room_id: int, session: AsyncSession = Depends(get_db)):
    """Получение информации о бронировании комнаты по её ID"""
    room = await get_booked_room_by_id(session, room_id)
    return {"room": room}

@router.get("/get-my-booked-rooms/{user_id}")
async def all_booking_rooms(request: Request, user_id: int, session: AsyncSession = Depends(get_db)):
    """Возвращает список всех комнат"""
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")

    if user_id != get_info_from_access_token(token, "user_id"):
        raise HTTPException(status_code=404, detail="Not Found")

    booking_list = await get_user_booking(session, user_id)
    return {"booking_rooms": booking_list}