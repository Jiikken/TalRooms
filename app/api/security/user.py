from datetime import datetime


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
        raise False

    if current_user["access_lvl"] <= 1 and booked_room["booked_by_id"] != user_id and booked_room["requested_by_id"] != user_id:
        raise False

    elif current_user["id"] != user_id and current_user["access_lvl"] <= 1:
        raise False
    return True

def formating_date(format_date: datetime) -> str:
    """Формирование даты для HTML"""
    months = ["января", "февраля", "марта", "апреля", "мая", "июня",
              "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    return f"{format_date.day} {months[format_date.month - 1]} {format_date.year}"