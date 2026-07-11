from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.connect import get_db
from app.core.database.crud.user import get_user_info, get_user_by_id_bd
from app.core.security.JWT import get_info_from_access_token

router = APIRouter(prefix="/user", tags=["User"])

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "frontend" / "templates")

@router.get("/get-role")
async def get_user_role(request: Request):
    """Получение роли пользователя"""
    token = request.cookies.get("access_token")
    role = get_info_from_access_token(token, "role")
    return {"role": role}

@router.get("/get-id")
async def get_user_id(request: Request):
    """Получение ID пользователя"""
    token = request.cookies.get("access_token")
    _id = get_info_from_access_token(token, "user_id")
    return {"user_id": _id}

@router.get("/get-user-by-id/{user_id}")
async def get_user_by_id(user_id: int, request: Request, session: AsyncSession = Depends(get_db)):
    """Получение пользователя по ID"""
    token = request.cookies.get("access_token")
    user_role = get_info_from_access_token(token, "role")
    if user_role < 1:
        raise HTTPException(status_code=404, detail="Not Found")

    return await get_user_by_id_bd(session, user_id)

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