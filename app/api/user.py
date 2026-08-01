from pathlib import Path

from fastapi import APIRouter, Body
from fastapi.templating import Jinja2Templates

from app.api.security.user import *
from app.core.database.crud.user import get_user_by_id_bd, get_hashed_password
from app.core.database.security import exists_user as exists_user_db
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
    exists = await exists_user_db(session, email)
    return {"exists": exists}

@router.get("/check/auth")
async def check_auth_user(request: Request):
    """Проверка пользователя на вход"""
    token = request.cookies.get("access_token")
    if token:
        return {"authenticated": True}
    return {"authenticated": False}

@router.post("/check/password")
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

@router.get("/my")
async def profile(request: Request, user: UserResponse = Depends(get_current_user)):
    """Страница профиля пользователя"""
    access_lvl = user.access_lvl
    date_register = user.created

    formed_date_register = date_register.strftime("%Y.%m.%d %H:%M")
    today_date = datetime.now().strftime("%d.%m.%Y")

    role = "Пользователь" if access_lvl == 0 else "Сотрудник" if access_lvl == 1 else "Администратор"
    active = "Активен"

    return templates.TemplateResponse(request,
                                      "profile.html",
                                      {"role": role,
                                       "is_active": active,
                                       "first_name": user.first_name,
                                       "last_name": user.last_name,
                                       "email": user.email,
                                       "date_register": formed_date_register,
                                       "today_date": today_date
                                       })