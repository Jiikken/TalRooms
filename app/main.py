from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import auth, user, booking_rooms
from app.core.database.connect import init_db, engine
from app.services.date import get_today_date_ymd, get_today_date_dmy


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()

app = FastAPI(title="TalRooms", lifespan=lifespan)
app.mount("/frontend/static", StaticFiles(directory=Path(__file__).parent / "frontend" / "static"), name="static")

templates = Jinja2Templates(directory=Path(__file__).parent / "frontend" / "templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница приложения"""
    today_date = get_today_date_dmy()
    return templates.TemplateResponse(request, "index.html", {"today_date": today_date})

@app.get("/ping")
async def ping():
    """Проверка работоспособности"""
    return {"status": "ok", "message": "pong"}

@app.get("/get/today")
async def get_date():
    """Получение сегодняшней даты"""
    today_date = get_today_date_ymd()
    return {"today_date": today_date}

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(booking_rooms.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )