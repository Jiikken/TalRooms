from fastapi import Request, Response

from app.core.security.JWT import create_access_token
from app.schemas.user import UserResponse


def _create_token(user: UserResponse) -> str:
    """Создание JWT токена"""
    return create_access_token({
        "email": user.email,
        "user_id": user.id,
        "role": user.access_lvl
    })

def _delete_cookies(request: Request, response: Response):
    """Удаление ненужных cookies"""
    if request.cookies.get("access_token"):
        response.delete_cookie("access_token")
    response.delete_cookie("access_token_reg")

def _set_cookies(response: Response, token: str):
    """Установка cookies"""
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800,
        path="/"
    )

def update_tokens_login(request: Request, response: Response, user: UserResponse) -> bool:
    """Обновление JWT токенов при авторизации"""
    token = _create_token(user)
    _delete_cookies(request, response)
    _set_cookies(response, token)
