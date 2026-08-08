from unittest.mock import patch

import pytest

from app.api.security.user import exists_parameters, exists_token, exists_user, exists_access_to_view, check_owner, \
    get_current_user
from tests.conftest import mock_session

class TestExists:
    @pytest.mark.parametrize("room_id, date, admin_id, expected", [
        (None, None, None, False),
        (1, "2024-01-01", 1, True),
        (None, "2024-01-01", 1, False),
        (1, None, 1, False),
        (1, "2024-01-01", None, False),
    ])
    def test_exists_parameters(self, room_id, date, admin_id, expected):
        """Тест: наличие всех параметров в ссылке"""
        assert exists_parameters(room_id, date, admin_id) == expected

    @pytest.mark.parametrize("token, expected", [
        (None, False),
        ("test_token", True),
        ("", False),
    ])
    def test_exists_token(self, token, expected):
        """Тест: проверка наличия токена"""
        assert exists_token(token) == expected

    @pytest.mark.parametrize("user, expected", [
        (None, False),
        ({"test": "test1"}, True),
        ({}, False),
    ])
    def test_exists_user(self, user, expected):
        """Тест: проверка наличия пользователя"""
        assert exists_user(user) == expected

    @pytest.mark.parametrize("room_fixture, user_fixture, user_id, expected", [
        # 1. Проверка на None
        (None, None, None, False),
        (None, "mock_user", 1, False),
        ("mock_booked_room", None, None, False),
        ("mock_booked_room", "mock_user", None, False),

        # 2. Пользователь (access_lvl=0)
        ("mock_booked_room", "mock_user", 1, True),
        ("mock_booked_room", "mock_user", 2, True),
        ("mock_booked_room", "mock_user", 5, False),

        # 3. Администратор (access_lvl=2)
        ("mock_booked_room", "mock_admin", 999, True),
        ("mock_booked_room", "mock_admin", None, False),
    ])
    def test_exists_access_to_view(self, request, room_fixture, user_fixture, user_id, expected):
        """Тест: наличие доступа у пользователя"""
        booked_room = request.getfixturevalue(room_fixture) if room_fixture else None
        current_user = request.getfixturevalue(user_fixture) if user_fixture else None

        assert exists_access_to_view(booked_room, current_user, user_id) == expected

class TestCheckOwner:
    @pytest.fixture
    def _cookies(self):
        return {"access_token": "test_token"}

    @pytest.mark.asyncio
    async def test_check_owner_with_all_tokens(self, mock_request, mock_session, mock_user):
        """Тест: проверка прав со всеми токенами (access_token, access_token_reg)"""
        mock_request.cookies = {"access_token": "test_token", "access_token_reg": "test_reg_token"}

        with patch("app.api.security.user.get_info_from_access_token") as mock_get_info, \
                patch("app.api.security.user.get_user_info") as mock_get_user:
            mock_get_info.return_value = 1
            mock_get_user.return_value = dict(mock_user)

            result = await check_owner(request=mock_request, session=mock_session)

            mock_get_info.assert_called_once_with("test_token", "user_id")
            mock_get_user.assert_called_once_with(mock_session, user_id=1)
            assert result == mock_user
            assert result.id == 1
            assert result.email == "test@example.com"


    @pytest.mark.asyncio
    async def test_check_owner_with_reg_token(self, mock_request, mock_user, mock_session):
        """Тест: проверка прав с access_token_reg"""
        mock_request.cookies = {"access_token_reg": "test_reg_token"}

        with patch("app.api.security.user.get_info_from_access_token") as mock_get_info, \
                patch("app.api.security.user.get_user_info") as mock_get_user:
            mock_get_info.return_value = 1
            mock_get_user.return_value = dict(mock_user)

            result = await check_owner(request=mock_request, session=mock_session)

            mock_get_info.assert_called_once_with("test_reg_token", "user_id")
            mock_get_user.assert_called_once_with(mock_session, user_id=1)
            assert result == mock_user
            assert result.id == 1
            assert result.email == "test@example.com"


    @pytest.mark.asyncio
    async def test_check_owner_with_access_token(self, mock_request, mock_user, mock_session, _cookies):
        """Тест: проверка прав с access_token"""
        mock_request.cookies = _cookies

        with patch("app.api.security.user.get_info_from_access_token") as mock_get_info, \
                patch("app.api.security.user.get_user_info") as mock_get_user:
            mock_get_info.return_value = 1
            mock_get_user.return_value = dict(mock_user)

            result = await check_owner(request=mock_request, session=mock_session)

            mock_get_info.assert_called_once_with("test_token", "user_id")
            mock_get_user.assert_called_once_with(mock_session, user_id=1)
            assert result == mock_user
            assert result.id == 1
            assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_check_owner_empty_cookies(self, mock_request, mock_session):
        """Тест: ошибка при пустых cookies"""
        mock_request.cookies = {}

        with pytest.raises(ValueError):
            await check_owner(request=mock_request, session=mock_session)


    @pytest.mark.asyncio
    async def test_check_owner_user_not_found(self, mock_request, mock_session, _cookies):
        """Тест: пользователь не найден"""
        mock_request.cookies = _cookies

        with patch("app.api.security.user.get_info_from_access_token") as mock_get_info, \
                patch("app.api.security.user.get_user_info") as mock_get_user:
            mock_get_info.return_value = 999
            mock_get_user.return_value = None

            with pytest.raises(Exception):
                await check_owner(request=mock_request, session=mock_session)


    @pytest.mark.asyncio
    async def test_check_owner_invalid_token(self, mock_request, mock_session, _cookies):
        """Тест: невалидный токен"""
        mock_request.cookies = _cookies

        with patch("app.api.security.user.get_info_from_access_token") as mock_get_info:
            mock_get_info.side_effect = ValueError("Invalid token")

            with pytest.raises(ValueError):
                await check_owner(request=mock_request, session=mock_session)


    @pytest.mark.asyncio
    async def test_check_owner_db_error(self, mock_request, mock_session, _cookies):
        """Тест: ошибка базы данных"""
        mock_request.cookies = _cookies

        with patch("app.api.security.user.get_info_from_access_token") as mock_get_info, \
                patch("app.api.security.user.get_user_info") as mock_get_user:
            mock_get_info.return_value = 1
            mock_get_user.side_effect = Exception("Database connection error")

            with pytest.raises(Exception, match="Database connection error"):
                await check_owner(request=mock_request, session=mock_session)

class TestGetCurrentUser:
    @pytest.fixture
    def _cookies(self):
        return {"access_token": "test_token"}

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_request, mock_session, mock_user, _cookies):
        """Тест: успешное получение текущего пользователя"""
        mock_request.cookies = _cookies

        with patch("app.api.security.user.get_info_from_access_token") as mock_get_info, \
                patch("app.api.security.user.get_user_info") as mock_get_user, \
                patch("app.api.security.user.UserResponse.model_validate") as mock_validate:
            mock_get_info.return_value = 1
            mock_get_user.return_value = {"id": 1, "first_name": "test1", "last_name": "test2"}
            mock_validate.return_value = mock_user

            result = await get_current_user(mock_request, mock_session)

            mock_get_info.assert_called_once_with("test_token", "user_id")
            mock_get_user.assert_called_once_with(mock_session, user_id=1)
            mock_validate.assert_called_once_with({"id": 1, "first_name": "test1", "last_name": "test2"})
            assert result == mock_user
            assert result.id == 1
            assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_empty_token(self, mock_request, mock_session):
        """Тест: access_token пустой"""
        mock_request.cookies = {"access_token": ""}

        with patch("app.api.security.user.get_info_from_access_token") as mock_get_info:
            mock_get_info.return_value = None

            with pytest.raises(ValueError) as exc_info:
                await get_current_user(mock_request, mock_session)

            assert "Пользователь не найден" in str(exc_info)
            mock_get_info.assert_called_once_with("", "user_id")

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_request, mock_session, _cookies):
        """Тест: невалидный токен"""
        mock_request.cookies = _cookies

        with patch("app.api.security.user.get_info_from_access_token") as mock_get_info:
            mock_get_info.side_effect = Exception("Invalid token")

            with pytest.raises(Exception) as exc_info:
                await get_current_user(mock_request, mock_session)

            assert "Invalid token" in str(exc_info.value)
            mock_get_info.assert_called_once_with("test_token", "user_id")

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self, mock_request, mock_session, _cookies):
        """Тест: токен валидный, но пользователь не найден в БД"""
        mock_request.cookies = _cookies

        with patch("app.api.security.user.get_info_from_access_token") as mock_get_info, \
                patch("app.api.security.user.get_user_info") as mock_get_user:
            mock_get_info.return_value = 999
            mock_get_user.return_value = None

            with pytest.raises(ValueError) as exc_info:
                await get_current_user(mock_request, mock_session)

            assert "Пользователь не найден" in str(exc_info)
            mock_get_info.assert_called_once_with("test_token", "user_id")
            mock_get_user.assert_called_once_with(mock_session, user_id=999)

    @pytest.mark.asyncio
    async def test_get_current_user_database_error(self, mock_request, mock_session, _cookies):
        """Тест: ошибка базы данных при получении пользователя"""
        mock_request.cookies = _cookies

        with patch("app.api.security.user.get_info_from_access_token") as mock_get_info, \
                patch("app.api.security.user.get_user_info") as mock_get_user:
            mock_get_info.return_value = 1
            mock_get_user.side_effect = Exception("Database connection error")

            with pytest.raises(Exception) as exc_info:
                await get_current_user(mock_request, mock_session)

            assert "Database connection error" in str(exc_info.value)
            mock_get_info.assert_called_once_with("test_token", "user_id")
            mock_get_user.assert_called_once_with(mock_session, user_id=1)


    @pytest.mark.asyncio
    async def test_get_current_user_user_response_validation_error(self, mock_request, mock_session, _cookies):
        """Тест: ошибка валидации UserResponse"""
        mock_request.cookies = _cookies

        with patch("app.api.security.user.get_info_from_access_token") as mock_get_info, \
                patch("app.api.security.user.get_user_info") as mock_get_user, \
                patch("app.api.security.user.UserResponse.model_validate") as mock_validate:
            mock_get_info.return_value = 1
            mock_get_user.return_value = {"invalid_field": "data"}
            mock_validate.side_effect = ValueError("Validation error")

            with pytest.raises(ValueError) as exc_info:
                await get_current_user(mock_request, mock_session)

            assert "Validation error" in str(exc_info.value)
            mock_validate.assert_called_once_with({"invalid_field": "data"})