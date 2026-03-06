"""OurGrid API client with Keycloak authentication."""
from __future__ import annotations

import time
from typing import Any

import aiohttp

from .const import BASE_URL


class OurGridApiError(Exception):
    """General API error."""


class OurGridAuthError(OurGridApiError):
    """Authentication failed (invalid credentials or token revoked)."""


class OurGridConnectionError(OurGridApiError):
    """Cannot reach the server."""


class OurGridApiClient:
    """Handles communication with the OpenRemote REST API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        realm: str,
        client_id: str,
        client_secret: str,
    ) -> None:
        self._session = session
        self._realm = realm
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0

    async def _async_ensure_token(self) -> None:
        """Obtain or refresh the access token when it is about to expire."""
        if self._access_token and time.monotonic() < self._token_expires_at - 30:
            return

        url = f"{BASE_URL}/auth/realms/{self._realm}/protocol/openid-connect/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

        try:
            async with self._session.post(url, data=data) as resp:
                if resp.status in (401, 403):
                    raise OurGridAuthError(
                        f"Authentication failed (HTTP {resp.status})"
                    )
                if resp.status != 200:
                    raise OurGridApiError(
                        f"Token request failed with HTTP {resp.status}"
                    )
                payload = await resp.json()
        except aiohttp.ClientError as err:
            raise OurGridConnectionError(f"Connection error: {err}") from err

        self._access_token = payload["access_token"]
        self._token_expires_at = time.monotonic() + payload.get("expires_in", 300)

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token}"}

    async def async_get_asset(self, asset_id: str) -> dict[str, Any]:
        """Fetch a single asset from the OpenRemote API."""
        await self._async_ensure_token()

        url = f"{BASE_URL}/api/{self._realm}/asset/{asset_id}"
        try:
            async with self._session.get(url, headers=self._auth_headers()) as resp:
                if resp.status in (401, 403):
                    self._access_token = None  # force re-auth on next call
                    raise OurGridAuthError(
                        f"Unauthorized when fetching asset {asset_id} (HTTP {resp.status})"
                    )
                if resp.status != 200:
                    raise OurGridApiError(
                        f"Failed to fetch asset {asset_id} (HTTP {resp.status})"
                    )
                return await resp.json()
        except aiohttp.ClientError as err:
            raise OurGridConnectionError(f"Connection error: {err}") from err

    async def async_write_attribute(
        self, asset_id: str, attribute_name: str, value: Any
    ) -> None:
        """Write a value to an asset attribute."""
        await self._async_ensure_token()

        url = f"{BASE_URL}/api/{self._realm}/asset/{asset_id}/attribute/{attribute_name}"
        try:
            async with self._session.put(
                url,
                headers=self._auth_headers(),
                json=value,
            ) as resp:
                if resp.status in (401, 403):
                    self._access_token = None
                    raise OurGridAuthError(
                        f"Unauthorized when writing attribute {attribute_name} (HTTP {resp.status})"
                    )
                if resp.status not in (200, 204):
                    raise OurGridApiError(
                        f"Failed to write attribute {attribute_name} (HTTP {resp.status})"
                    )
        except aiohttp.ClientError as err:
            raise OurGridConnectionError(f"Connection error: {err}") from err

    async def async_test_connection(self, challenge_asset_id: str) -> None:
        """Validate credentials by fetching the challenge asset. Raises on failure."""
        await self._async_ensure_token()
        await self.async_get_asset(challenge_asset_id)
