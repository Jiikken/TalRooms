from datetime import datetime, timedelta, timezone
from app.core.config import config
import jwt

jwt_info = config.get_jwt_info()

def create_access_token(data: dict) -> str:
    """Создание JWT токена"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=float(jwt_info.get("access_token_expire_minutes")))
    data.update({"exp": expire})
    return jwt.encode(data, jwt_info.get("secret_key"), algorithm=jwt_info.get("algorithm"))

def get_info_from_access_token(token: str, out: str):
    payload = jwt.decode(token, jwt_info.get("secret_key"), algorithms=[jwt_info.get("algorithm")])
    return payload.get(f"{out}")