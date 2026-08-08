from unittest.mock import patch

from app.api.security.cookies import update_tokens_login


def test_update_tokens_login_success(
        mock_user,
        mock_request,
        mock_response
):
    """Тест: все внутренние функции вызываются с правильными параметрами"""

    expected_token = {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token"
    }

    with patch('app.api.security.cookies._create_token') as mock_create_token, \
        patch('app.api.security.cookies._delete_cookies') as mock_delete_cookies, \
        patch('app.api.security.cookies._set_cookies') as mock_set_cookies:

        mock_create_token.return_value = expected_token

        mock_delete_cookies.return_value = None
        mock_set_cookies.return_value = None

        mock_request.cookies = {"access_token": "old_token", "refresh_token": "old_refresh"}

        update_tokens_login(
            request=mock_request,
            response=mock_response,
            user=mock_user
        )

        mock_create_token.assert_called_once_with(mock_user)
        mock_delete_cookies.assert_called_once_with(mock_request, mock_response)
        mock_set_cookies.assert_called_once_with(mock_response, expected_token)

        assert mock_create_token.call_count == 1
        assert mock_delete_cookies.call_count == 1
        assert mock_set_cookies.call_count == 1
        assert mock_create_token.called_before(mock_delete_cookies)
        assert mock_delete_cookies.called_before(mock_set_cookies)