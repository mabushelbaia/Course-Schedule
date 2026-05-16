import asyncio
import re
from urllib.parse import urlencode

import httpx


FLARESOLVERR_DEFAULT = "http://localhost:8191/v1"
BASE_URL = "https://ritaj.birzeit.edu"
LOGIN_URL = f"{BASE_URL}/register/"
SCHEDULE_URL = f"{BASE_URL}/instructor/schedule"
CALENDAR_URL = f"{BASE_URL}/academic-calendar?lang=en"


def _extract_hidden_fields(html: str) -> dict:
    fields = {}
    for name in [
        "form:mode", "form:id", "__confirmed_p", "__refreshing_p",
        "return_url", "time", "token_id", "hash",
    ]:
        m = re.search(rf'name="{re.escape(name)}"\s+value="([^"]*)"', html)
        if m:
            fields[name] = m.group(1)
    return fields


class RitajError(Exception):
    pass


async def fetch_academic_calendar(flaresolverr_url: str = FLARESOLVERR_DEFAULT) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        payload = {"cmd": "request.get", "url": CALENDAR_URL, "maxTimeout": 60000}
        resp = await client.post(flaresolverr_url, json=payload)
        data = resp.json()
        if data.get("status") != "ok":
            raise RitajError(f"FlareSolverr error: {data.get('message', data)}")
        return data["solution"]["response"]


class RitajClient:
    def __init__(
        self,
        flaresolverr_url: str = FLARESOLVERR_DEFAULT,
        username: str | None = None,
        password: str | None = None,
    ):
        self.flaresolverr_url = flaresolverr_url
        self.username = username
        self.password = password
        self._session_name = f"ritaj-schedule-{id(self)}"
        self._client = httpx.AsyncClient(timeout=120)

    async def _flaresolverr(self, cmd: str, **kwargs) -> dict:
        payload = {"cmd": cmd, "session": self._session_name, **kwargs}
        resp = await self._client.post(self.flaresolverr_url, json=payload)
        data = resp.json()
        if data.get("status") != "ok":
            raise RitajError(f"FlareSolverr error: {data.get('message', data)}")
        return data

    async def _wait_for_flaresolverr(self, retries: int = 15, delay: int = 3) -> None:
        for attempt in range(retries):
            try:
                await self._flaresolverr("sessions.list")
                return
            except (httpx.ConnectError, httpx.RemoteProtocolError, RitajError):
                if attempt == retries - 1:
                    raise RitajError(
                        f"Could not connect to FlareSolverr at {self.flaresolverr_url} "
                        f"after {retries} attempts."
                    )
                await asyncio.sleep(delay)

    async def login(self) -> None:
        if not self.username or not self.password:
            raise RitajError("username and password must be set.")

        await self._wait_for_flaresolverr()

        result = await self._flaresolverr("request.get", url=LOGIN_URL, maxTimeout=60000)
        html = result["solution"]["response"]
        fields = _extract_hidden_fields(html)

        fields["username"] = self.username
        fields["password"] = self.password
        body = urlencode(fields)

        result = await self._flaresolverr(
            "request.post", url=LOGIN_URL, postData=body, maxTimeout=60000,
        )
        response = result["solution"]["response"]
        # If login page is returned again (contains hidden fields), login failed
        if _extract_hidden_fields(response):
            raise RitajError("Login failed — check credentials.")

    async def fetch_schedule(self) -> str:
        result = await self._flaresolverr("request.get", url=SCHEDULE_URL, maxTimeout=60000)
        return result["solution"]["response"]

    async def fetch_academic_calendar(self) -> str:
        result = await self._flaresolverr("request.get", url=CALENDAR_URL, maxTimeout=60000)
        return result["solution"]["response"]

    async def close(self) -> None:
        try:
            await self._flaresolverr("sessions.destroy")
        except Exception:
            pass
        await self._client.aclose()
