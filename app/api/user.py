from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, Depends, HTTPException, Body
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.connect import get_db
from app.core.database.crud.rooms_booking import get_room_by_id, get_booked_room_by_room_id_and_date
from app.core.database.crud.user import get_user_info, get_user_by_id_bd, get_hashed_password
from app.core.database.security import exists_user
from app.core.security.JWT import get_info_from_access_token
from app.core.security.password import check_password

router = APIRouter(prefix="/user", tags=["User"])

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "frontend" / "templates")

@router.get("/get/role")
async def get_user_role(request: Request):
    """Получение роли пользователя"""
    token = request.cookies.get("access_token")
    role = get_info_from_access_token(token, "role")
    return {"role": role}

@router.get("/get/id")
async def get_user_id(request: Request):
    """Получение ID пользователя"""
    token = request.cookies.get("access_token")
    _id = get_info_from_access_token(token, "user_id")
    return {"user_id": _id}

@router.get("/get/email")
async def get_email_user(request: Request):
    """Получение email из access_token"""
    token = request.cookies.get("access_token")
    return get_info_from_access_token(token, "email")

@router.post("/check-user")
async def check_exists_user(session: AsyncSession = Depends(get_db), email: str = Body(..., embed=True)):
    """Проверка существования пользователя в базе данных"""
    exists = await exists_user(session, email)
    return {"exists": exists}

@router.get("/check-auth")
async def check_auth_user(request: Request):
    """Проверка пользователя на вход"""
    token = request.cookies.get("access_token")
    if token:
        return {"authenticated": True}
    return {"authenticated": False}

@router.post("/check-password")
async def check_password_user(session: AsyncSession = Depends(get_db), email: str = Body(...), password: bytes = Body(...)):
    """Проверка правильности пароля"""
    hashed_password = await get_hashed_password(session, email)
    return check_password(password, hashed_password.encode('utf-8'))

@router.get("/get/user-by-id/{user_id}")
async def get_user_by_id(user_id: int, request: Request, session: AsyncSession = Depends(get_db)):
    """Получение пользователя по ID"""
    token = request.cookies.get("access_token")
    user_role = get_info_from_access_token(token, "role")
    if user_role < 1:
        raise HTTPException(status_code=404, detail="Not Found")

    return await get_user_by_id_bd(session, user_id)

@router.get("/profile/{user_id}/booked-room/{room_id}")
async def booked_room(request: Request, user_id: int, room_id: int, date: str | None = None, admin_id: int | None = None, session: AsyncSession = Depends(get_db)):
    """Страница деталей бронированной комнаты"""
    if room_id is None or date is None or admin_id is None:
        raise HTTPException(status_code=404, detail="Not Found")

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")

    email = get_info_from_access_token(token, "email")

    info_user = await get_user_by_id_bd(session, user_id)
    if not info_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    current_user = await get_user_info(session, email)
    format_date = datetime.strptime(date, "%Y-%m-%d")
    _booked_room = await get_booked_room_by_room_id_and_date(session, room_id, format_date)
    if _booked_room is None:
        raise HTTPException(status_code=404, detail="Not Found")

    if current_user["access_lvl"] <= 1 and _booked_room["booked_by_id"] != user_id and _booked_room["requested_by_id"] != user_id:
        raise HTTPException(status_code=404, detail="Not Found")

    elif current_user["id"] != user_id and current_user["access_lvl"] <= 1:
        raise HTTPException(status_code=404, detail="Not Found")

    today_date = datetime.now().strftime("%d.%m.%Y")
    months = ["января", "февраля", "марта", "апреля", "мая", "июня",
              "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    result_date = f"{format_date.day} {months[format_date.month - 1]} {format_date.year}"
    return templates.TemplateResponse(request, "booked_room.html", context={"booking_date": result_date,
                                                                            "today_date": today_date,
                                                                            "booked_by_id": admin_id,
                                                                            "booking_date_service": date})

@router.get("/profile/{user_id}")
async def profile(request: Request, user_id: int, session: AsyncSession = Depends(get_db)):
    """Страница профиля пользователя"""
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")

    email = get_info_from_access_token(token, "email")

    info_user = await get_user_by_id_bd(session, user_id)
    if not info_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    current_user = await get_user_info(session, email)
    if current_user["id"] != user_id:
        raise HTTPException(status_code=404, detail="Страница не найдена")

    access_lvl = get_info_from_access_token(token, "role")
    date_register = info_user.get("created")
    formed_date_register = date_register.strftime("%Y.%m.%d %H:%M")
    today_date = datetime.now().strftime("%d.%m.%Y")

    role = "Пользователь" if access_lvl == 0 else "Сотрудник" if access_lvl == 1 else "Администратор"
    active = "Активен" if info_user.get("is_active") is True else "Не активен"

    return templates.TemplateResponse(request,
                                      "profile.html",
                                      {"role": role,
                                       "is_active": active,
                                       "first_name": info_user.get("first_name"),
                                       "last_name": info_user.get("last_name"),
                                       "email": email,
                                       "date_register": formed_date_register,
                                       "today_date": today_date
                                       })