from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

from fastapi import APIRouter, Request, Form, Response
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.security.user import check_owner
from app.core.database.connect import get_db
from app.core.database.crud.user import create_user, update_user_activity
from app.core.security.JWT import create_access_token
from app.schemas.user import UserCreate, UserResponse

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

@router.post("/register-user", response_model=UserResponse)
async def register_user(response: Response, request: Request, user: UserCreate, session: AsyncSession = Depends(get_db)):
    """Регистрация пользователя"""
    new_user = await create_user(user, session)

    if request.cookies.get("access_token_reg"):
        response.delete_cookie("access_token_reg")
    token = create_access_token({"user_id": new_user.id})
    response.set_cookie(key="access_token_reg", value=token, httponly=True)

    return UserResponse.model_validate(new_user)

@router.get("/success-register/{user_id}")
async def success_register(request: Request, current_user: UserResponse = Depends(check_owner)):
    """Страница успешной регистрации пользователя"""
    return templates.TemplateResponse(request,
                                      "success_register.html",
                                      context={"firstname": current_user.first_name,
                                               "lastname": current_user.last_name,
                                               "email": current_user.email})

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

    if request.cookies.get("access_token"):
        response.delete_cookie("access_token")

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800,
        path="/"
    )
    response.delete_cookie("access_token_reg")

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

@router.post("/logout")
async def logout_user(response: Response):
    """Выход из аккаунта"""
    response.delete_cookie("access_token")
    return {"message": "Logged out"}