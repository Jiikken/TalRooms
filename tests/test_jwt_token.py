from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from app.core.security.JWT import create_access_token, get_info_from_access_token

class TestToken:
    @pytest.fixture
    def _token(self):
        return create_access_token({"user_id": 1, "login": "test123"})

    def test_token_returns_string(self, _token):
        """Проверка на то, чтобы JWT токен был строкой"""
        assert isinstance(_token, str)
        assert len(_token) > 0

    def test_create_token_contains_data(self, _token):
        """Проверка на сохранение и получения данных в токене"""
        assert get_info_from_access_token(_token, "user_id") == 1
        assert get_info_from_access_token(_token, "login") == "test123"

    def test_auto_append_exp_time(self, _token):
        """Проверка на автоматическое добавление времени действия токена"""
        assert get_info_from_access_token(_token, "exp")

    def test_nonexistent_key_in_token(self, _token):
        """Проверка на получение несуществующего ключа"""
        assert get_info_from_access_token(_token, "nonexistent") is None

    def test_invalid_token(self):
        """Проверка на внесение невалидного токена"""
        with pytest.raises(Exception):
            get_info_from_access_token("token.is.invalid", "user_id")

    def test_create_access_token_expiration_time(self):
        """Проверяем, что токен истекает через правильное время"""
        with patch('app.core.security.JWT.datetime') as mock_datetime:
            fixed_now = datetime(2026, 8, 3, 10, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = fixed_now
            mock_datetime.timezone = timezone
            mock_datetime.timedelta = timedelta

            token = create_access_token({"user": "test_user"})

            import jwt
            from app.core.config import config

            jwt_info = config.get_jwt_info()

            payload = jwt.decode(
                token,
                jwt_info.get("secret_key"),
                algorithms=jwt_info.get("algorithm"),
                options={"verify_exp": False}
            )

            expire = payload.get("exp")

            exp_time = datetime.fromtimestamp(expire, tz=timezone.utc)
            expected_exp = fixed_now + timedelta(minutes=30)
            assert exp_time == expected_exp