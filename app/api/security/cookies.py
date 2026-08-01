from fastapi import Request, Response

from app.core.security.JWT import create_access_token
from app.schemas.user import UserResponse


def update_tokens_login(request: Request, response: Response, user: UserResponse):
    """Обновление JWT токенов при авторизации"""
    token = create_access_token({
        "email": user.email,
        "user_id": user.id,
        "role": user.access_lvl
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