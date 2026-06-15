"""Tests for MoodleClient (Task 6.1).

Uses unittest.mock.patch for httpx.AsyncClient since no pytest-httpx
is installed. Tests cover: successful API call, error response, timeout,
retry logic, and empty course.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.integrations.moodle_ws import MoodleClient, MoodleException


@pytest.fixture
def client():
    return MoodleClient(
        base_url="https://moodle.example.com",
        token="test-token-123",
        timeout=10,
        max_retries=2,
    )


def build_mock_response(data, status=200):
    """Helper to create a mock httpx.Response.

    httpx.Response.raise_for_status() and .json() are SYNCHRONOUS
    methods, so we use MagicMock (not AsyncMock) for them.
    """
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = data
    resp.raise_for_status.return_value = None
    if status >= 400:
        resp.raise_for_status.side_effect = Exception(f"HTTP {status}")
    return resp


def _make_moodle_mock(get_return=None, get_side_effect=None):
    """Create mock for httpx.AsyncClient context manager.

    Returns a dict with the mock class, the mock instance, and helper
    to inspect calls.
    """
    mock_instance = AsyncMock()
    mock_instance.__aenter__.return_value = mock_instance

    if get_side_effect is not None:
        mock_instance.get.side_effect = get_side_effect
    else:
        mock_instance.get.return_value = get_return

    mock_class = MagicMock(return_value=mock_instance)
    return mock_instance, mock_class


class TestMoodleClientInit:
    def test_strips_trailing_slash(self):
        c = MoodleClient("https://moodle.test/", "tok")
        assert c.base_url == "https://moodle.test"

    def test_keeps_url_without_slash(self):
        c = MoodleClient("https://moodle.test", "tok")
        assert c.base_url == "https://moodle.test"


class TestSyncUsuarios:
    async def test_returns_mapped_users(self, client):
        """Successful API call returns mapped user fields."""
        moodle_users = [
            {
                "firstname": "Juan",
                "lastname": "Pérez",
                "email": "juan@test.com",
                "groups": [{"name": "Comisión A", "id": 1}],
                "department": "CABA",
            },
            {
                "firstname": "María",
                "lastname": "García",
                "email": "maria@test.com",
                "groups": [],
                "department": "GBA",
            },
        ]

        mock_instance, mock_class = _make_moodle_mock(
            get_return=build_mock_response(moodle_users)
        )

        with patch("app.integrations.moodle_ws.httpx.AsyncClient", mock_class):
            result = await client.sync_usuarios(42)

        assert len(result) == 2
        assert result[0]["nombre"] == "Juan"
        assert result[0]["apellidos"] == "Pérez"
        assert result[0]["email"] == "juan@test.com"
        assert result[0]["comision"] == "Comisión A"
        assert result[0]["regional"] == "CABA"
        assert result[1]["comision"] is None
        assert result[1]["regional"] == "GBA"

    async def test_empty_course_returns_empty_list(self, client):
        mock_instance, mock_class = _make_moodle_mock(
            get_return=build_mock_response([])
        )

        with patch("app.integrations.moodle_ws.httpx.AsyncClient", mock_class):
            result = await client.sync_usuarios(1)

        assert result == []

    async def test_uses_correct_ws_function_and_course_id(self, client):
        mock_instance, mock_class = _make_moodle_mock(
            get_return=build_mock_response([])
        )

        with patch("app.integrations.moodle_ws.httpx.AsyncClient", mock_class):
            await client.sync_usuarios(99)

        call_kwargs = mock_instance.get.call_args
        assert call_kwargs is not None
        url = call_kwargs[0][0]
        params = call_kwargs[1]["params"]
        assert "core_enrol_get_enrolled_users" in str(params)
        assert params["courseid"] == 99
        assert params["wstoken"] == "test-token-123"
        assert params["moodlewsrestformat"] == "json"

    async def test_no_groups_sets_comision_to_none(self, client):
        mock_instance, mock_class = _make_moodle_mock(
            get_return=build_mock_response([
                {"firstname": "Ana", "lastname": "López", "email": "ana@test.com", "groups": None, "department": None},
            ])
        )

        with patch("app.integrations.moodle_ws.httpx.AsyncClient", mock_class):
            result = await client.sync_usuarios(1)

        assert result[0]["comision"] is None
        assert result[0]["regional"] is None


class TestSyncActividades:
    async def test_returns_empty_list_stub(self, client):
        result = await client.sync_actividades(1)
        assert result == []


class TestRequest:
    async def test_raises_moodle_exception_on_http_error(self, client):
        """HTTP error from get() call -> MoodleException."""
        mock_instance, mock_class = _make_moodle_mock(
            get_side_effect=Exception("HTTP 500")
        )

        with patch("app.integrations.moodle_ws.httpx.AsyncClient", mock_class):
            with pytest.raises(MoodleException) as exc_info:
                await client._request("core_enrol_get_enrolled_users", courseid=1)

        assert exc_info.value.status_code == 502

    async def test_raises_moodle_exception_on_moodle_error_response(self, client):
        """Moodle WS returns error JSON -> MoodleException."""
        error_data = {"exception": "moodle_exception", "message": "Invalid course"}
        mock_instance, mock_class = _make_moodle_mock(
            get_return=build_mock_response(error_data)
        )

        with patch("app.integrations.moodle_ws.httpx.AsyncClient", mock_class):
            with pytest.raises(MoodleException) as exc_info:
                await client._request("core_enrol_get_enrolled_users", courseid=999)

        assert "Invalid course" in str(exc_info.value.message)

    async def test_retries_on_timeout_and_succeeds(self, client):
        """Retry logic: transient timeout then success."""
        mock_instance = AsyncMock()
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.get.side_effect = [
            __import__("httpx").TimeoutException("timeout"),
            build_mock_response([{"firstname": "Juan", "lastname": "Pérez", "email": "j@t.com"}]),
        ]
        mock_class = MagicMock(return_value=mock_instance)

        with patch("app.integrations.moodle_ws.httpx.AsyncClient", mock_class):
            result = await client.sync_usuarios(1)

        assert len(result) == 1
        assert mock_instance.get.call_count == 2

    async def test_raises_moodle_exception_after_all_retries_exhausted(self, client):
        """Timeout persists -> MoodleException after all retries."""
        mock_instance, mock_class = _make_moodle_mock(
            get_side_effect=__import__("httpx").TimeoutException("timeout")
        )

        with patch("app.integrations.moodle_ws.httpx.AsyncClient", mock_class):
            with pytest.raises(MoodleException) as exc_info:
                await client._request("some_function")

        assert exc_info.value.retry_after == 60

    async def test_does_not_retry_on_non_transient_http_error(self, client):
        """HTTP errors should NOT be retried (only TimeoutException is transient)."""
        mock_instance, mock_class = _make_moodle_mock(
            get_side_effect=Exception("HTTP 403")
        )

        with patch("app.integrations.moodle_ws.httpx.AsyncClient", mock_class):
            with pytest.raises(MoodleException):
                await client._request("some_function")

        assert mock_instance.get.call_count == 1
