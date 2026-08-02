from datetime import datetime

def get_today_date_ymd() -> str:
    """Получение текущей даты"""
    return datetime.now().strftime("%Y-%m-%d")

def get_today_date_dmy() -> str:
    """Получение текущей даты"""
    return datetime.now().strftime("%d.%m.%Y")
