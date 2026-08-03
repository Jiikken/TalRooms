from datetime import datetime

def get_today_date_ymd() -> str:
    """Получение текущей даты"""
    return datetime.now().strftime("%Y-%m-%d")

def get_today_date_dmy() -> str:
    """Получение текущей даты"""
    return datetime.now().strftime("%d.%m.%Y")

def formating_date(format_date: datetime) -> str:
    """Формирование даты для HTML"""
    months = ["января", "февраля", "марта", "апреля", "мая", "июня",
              "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    return f"{format_date.day} {months[format_date.month - 1]} {format_date.year}"
