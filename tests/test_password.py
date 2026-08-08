import pytest

from app.core.security.password import hash_password, check_password


class TestPassword:
    @pytest.fixture
    def _password(self):
        return "test123"

    @pytest.fixture
    def _hashed(self, _password):
        return hash_password(_password)

    def test_hash_password_returns_string(self, _hashed):
        """Тест: хеш = строка"""
        assert isinstance(_hashed, str)
        assert len(_hashed) > 0

    def test_hashes_password_creates_different_hashed(self, _password):
        """Тест: хеш одинаковых паролей был разный (проверка на соль)"""
        hash1 = hash_password(_password)
        hash2 = hash_password(_password)
        assert hash1 != hash2

    def test_hash_password_length(self, _hashed):
        """Тест: длина хеша пароля (стандарт - 60)"""
        assert len(_hashed) == 60

    def test_password_correct(self, _hashed, _password):
        """Тест: правильность пароля"""
        assert check_password(_password.encode("utf-8"), _hashed.encode("utf-8")) is True

    def test_password_incorrect(self, _hashed):
        """Тест: неправильный пароль"""
        incorrect_password = "test12"

        assert check_password(incorrect_password.encode("utf-8"), _hashed.encode("utf-8")) is False

    def test_check_password_empy(self):
        """Тест: пустой пароль"""
        hashed_password = hash_password("")

        assert check_password(b"", hashed_password.encode("utf-8")) is True
        assert check_password(b" ", hashed_password.encode("utf-8")) is False