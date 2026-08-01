from datetime import datetime

from fastapi import Request, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.connect import get_db
from app.core.database.crud.user import get_user_info
from app.core.security.JWT import get_info_from_access_token
from app.schemas.user import UserResponse


def exists_parameters(room_id: int, date: str, admin_id: int) -> bool:
    """Проверка на наличие параметров ссылки"""
    if room_id is None or date is None or admin_id is None:
        return False
    return True

def exists_token(token: str) -> bool:
    """Проверка на наличие токена"""
    if not token:
        return False
    return True

def exists_user(user: dict) -> bool:
    """Проверка на наличие пользователя в системе"""
    if not user:
        return False
    return True

def exists_access_to_view(booked_room: dict, current_user: dict, user_id: int) -> bool:
    """Проверка на наличие прав для просмотра у пользователя"""
    if booked_room is None:
        return False

    if current_user["access_lvl"] <= 1 and booked_room["booked_by_id"] != user_id and booked_room["requested_by_id"] != user_id:
        return False

    elif current_user["id"] != user_id and current_user["access_lvl"] <= 1:
        return False
    return True

def formating_date(format_date: datetime) -> str:
    """Формирование даты для HTML"""
    months = ["января", "февраля", "марта", "апреля", "мая", "июня",
              "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    return f"{format_date.day} {months[format_date.month - 1]} {format_date.year}"

async def check_owner(request: Request, user_id: int, session: AsyncSession = Depends(get_db)):
    """Проверка прав на просмотр страницы"""
    token = None
    if request.cookies.get("access_token_reg"):
        token = request.cookies.get("access_token_reg")
    if request.cookies.get("access_token"):
        token = request.cookies.get("access_token")

    current_user_id = get_info_from_access_token(token, "user_id")
    current_user = await get_user_info(session, user_id=current_user_id)

    if current_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="У Вас нет доступа к этой странице")
    return UserResponse(**current_user)

async def get_current_user(request: Request, session: AsyncSession = Depends(get_db)):
    """Получение текущего пользователя"""
    token = request.cookies.get("access_token")
    user_id = get_info_from_access_token(token, "user_id")
    current_user = await get_user_info(session, user_id=user_id)

    return UserResponse.model_validate(current_user)
