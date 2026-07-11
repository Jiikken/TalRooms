import bcrypt

def hash_password(password: str) -> str:
    """Хеширование пароля"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: bytes, hashed: bytes) -> bool:
    """Проверка на правильность введённого пароля"""
    return bcrypt.checkpw(password, hashed)

