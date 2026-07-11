from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

from fastapi import APIRouter, Request, Form, Body, Response
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.connect import get_db
from app.core.database.crud.user import create_user, get_hashed_password, update_user_activity
from app.core.database.security import exists_user
from app.core.security.JWT import create_access_token, get_info_from_access_token
from app.core.security.password import check_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "frontend" / "templates")

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Страница входа в аккаунт"""
    return templates.TemplateResponse(request, "login.html")

@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    """Страница регистрации"""
    return templates.TemplateResponse(request, "register.html")

@router.post("/check-user")
async def check_exists_user(session: AsyncSession = Depends(get_db), email: str = Body(..., embed=True)):
    """Проверка существования пользователя в базе данных"""
    exists = await exists_user(session, email)
    return {"exists": exists}

@router.post("/register-user")
async def register_user(request: Request, session: AsyncSession = Depends(get_db),
                        firstname: str = Form(..., alias="firstName"),
                        lastname: str = Form(..., alias="lastName"),
                        email: str = Form(...),
                        password: str = Form(...)):
    """Страница успешной регистрации нового пользователя"""
    try:
        await create_user(firstname, lastname, email, password, session)
        return templates.TemplateResponse(request, "success_register.html",
                                          {"firstname": firstname,
                                                "lastname": lastname,
                                                "email": email})
    except ValueError:
        return templates.TemplateResponse(request, "register.html")

@router.post("/login-user")
async def login_user(request: Request, response: Response, email: str = Form(...), session: AsyncSession = Depends(get_db)):
    """Страница успешной авторизации пользователя"""
    now = datetime.now(timezone.utc)
    utctime_and_date_now = now.strftime("%Y.%m.%d %H:%M")
    email = unquote(email)
    user = await update_user_activity(session, email, is_active=True, last_login=utctime_and_date_now)
    user_id = user.get("id")
    token = create_access_token({
        "email": email,
        "user_id": user_id,
        "role": user.get("access_lvl")
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800,
        path="/"
    )

    return templates.TemplateResponse(request,
                                      "success_login.html",
                                      {"firstname": user.get("first_name"),
                                       "lastname": user.get("last_name"),
                                       "email": email,
                                       "last_login": user.get("last_login"),
                                       "user_id": user_id
                                       },
                                      headers=response.headers
                                      )

@router.get("/get/email")
async def get_email_user(request: Request):
    token = request.cookies.get("access_token")
    return get_info_from_access_token(token, "email")

@router.post("/logout")
async def logout_user(response: Response):
    """Выход из аккаунта"""
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

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