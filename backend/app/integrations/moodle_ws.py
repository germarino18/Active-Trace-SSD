"""Moodle Web Services client (C-09 Task 6.1).

Provides MoodleClient for interacting with Moodle WS API.
Uses httpx.AsyncClient with configurable timeout and retry.
"""

import httpx


class MoodleException(Exception):
    def __init__(self, message: str, status_code: int = 502, retry_after: int = 30):
        self.message = message
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(self.message)


class MoodleClient:
    """Client for Moodle Web Services API."""

    def __init__(self, base_url: str, token: str, timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries

    async def sync_usuarios(self, course_id: int) -> list[dict]:
        """Fetch enrolled users from a Moodle course.

        Returns list of dicts with: nombre, apellidos, email, comision, regional.
        Maps Moodle WS fields:
        - firstname -> nombre
        - lastname -> apellidos
        - email -> email
        - groups -> comision (first group name if any)
        - department -> regional

        Uses core_enrol_get_enrolled_users WS function.
        """
        data = await self._request("core_enrol_get_enrolled_users", courseid=course_id)
        result = []
        for user in data:
            result.append({
                "nombre": user.get("firstname", ""),
                "apellidos": user.get("lastname", ""),
                "email": user.get("email"),
                "comision": self._extract_group_name(user.get("groups")),
                "regional": user.get("department"),
            })
        return result

    async def sync_actividades(self, course_id: int) -> list[dict]:
        """Stub for C-10: fetch activities from a Moodle course."""
        _ = course_id
        return []

    @staticmethod
    def _extract_group_name(groups: list | None) -> str | None:
        if groups and len(groups) > 0:
            return groups[0].get("name")
        return None

    async def _request(self, wsfunction: str, **params) -> dict | list:
        """Make authenticated request to Moodle WS API with retry logic.

        Uses httpx.AsyncClient with timeout.
        Retries on TimeoutException up to max_retries.
        Raises MoodleException on failure.
        """
        params["wstoken"] = self.token
        params["wsfunction"] = wsfunction
        params["moodlewsrestformat"] = "json"

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(
                        f"{self.base_url}/webservice/rest/server.php",
                        params=params,
                    )
                    response.raise_for_status()
                    data = response.json()
                    if isinstance(data, dict) and "exception" in data:
                        raise MoodleException(
                            data.get("message", "Moodle WS error"),
                            status_code=502,
                        )
                    return data
            except httpx.TimeoutException:
                if attempt == self.max_retries - 1:
                    raise MoodleException(
                        "Moodle timeout",
                        status_code=502,
                        retry_after=60,
                    )
            except MoodleException:
                raise
            except Exception as e:
                raise MoodleException(
                    f"Moodle request failed: {e}",
                    status_code=502,
                )
