import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from unittest.mock import MagicMock, AsyncMock
from fastapi.responses import HTMLResponse

import pytest
from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserResponse


@pytest.fixture
def mock_user():
    """Фикстура: тестовый пользователь"""
    return UserResponse(
        id=1,
        first_name="User1",
        last_name="User2",
        email="test@example.com", # type: ignore
        access_lvl=0,
        last_login="2026-08-04T10:00:00",
        created="2026-01-01T10:00:00", # type: ignore
    )

@pytest.fixture
def mock_admin():
    """Фикстура: тестовый администратор"""
    return UserResponse(
        id=2,
        first_name="Admin1",
        last_name="Admin2",
        email="test@example.com", # type: ignore
        access_lvl=2,
        last_login="2026-08-04T10:00:00",
        created="2026-01-01T10:00:00", # type: ignore
    )

@pytest.fixture
def mock_booked_room():
    """Фикстура: забронированная комната"""
    return {"room_id": 1,
            "booked_by_id": 2,
            "requested_by_id": 1}

@pytest.fixture
def mock_request():
    """Фикстура: мок Request"""
    request = MagicMock(spec=Request)
    request.cookies = {}
    return request

@pytest.fixture
def mock_response():
    """Фикстура: мок Response"""
    response = MagicMock(spec=Response)
    response.delete_cookie = MagicMock()
    response.set_cookie = MagicMock()
    return response

@pytest.fixture
def mock_session():
    """Фикстура: мок AsyncSession"""
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_templates():
    """Фикстура: мок шаблона HTML"""
    mock_templates = MagicMock()
    mock_templates.TemplateResponse.return_value = HTMLResponse(content="<html>test</html>")
    return mock_templates