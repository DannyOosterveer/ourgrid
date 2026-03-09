"""DataUpdateCoordinator for the OurGrid integration."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from homeassistant.util import dt as dt_util

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OurGridApiClient, OurGridAuthError, OurGridApiError, OurGridConnectionError
from .const import (
    ATTR_CHALLENGE_EARNINGS,
    ATTR_CHALLENGE_END,
    ATTR_CHALLENGE_POINTS,
    ATTR_CHALLENGE_POINTS_CURRENT,
    ATTR_CHALLENGE_POINTS_EXCHANGE_RATE,
    ATTR_CHALLENGE_POWER_LIMIT,
    ATTR_CHALLENGE_START,
    ATTR_CHALLENGE_STATUS,
    ATTR_CHALLENGES_JOINED,
    ATTR_CONNECTION_QUALITY,
    ATTR_CONNECTION_STATUS,
    ATTR_POWER,
    ATTR_PEAK_POINTS,
    ATTR_TOTAL_POINTS,
    ATTR_WIFI_SIGNAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class OurGridData:
    """Snapshot of all OurGrid sensor values."""

    challenge_start: datetime | None
    challenge_end: datetime | None
    challenge_points_exchange_rate: float | None
    challenge_status: str | None
    challenge_power_limit: float | None
    power: float | None
    # Points & earnings
    challenge_earnings: float | None
    challenges_joined: float | None
    total_points: float | None
    challenge_points_current: float | None
    challenge_points: float | None
    peak_points: float | None
    # Connectivity (diagnostic)
    connection_quality: float | None
    connection_status: str | None
    wifi_signal: float | None


def _attr_value(raw: dict, attr_name: str):
    """Extract the value of an OpenRemote attribute from a raw asset dict."""
    return raw.get("attributes", {}).get(attr_name, {}).get("value")


def _parse_float(raw: dict, attr_name: str) -> float | None:
    val = _attr_value(raw, attr_name)
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _parse_bool(raw: dict, attr_name: str) -> bool | None:
    val = _attr_value(raw, attr_name)
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() == "true"
    return bool(val)


def _parse_datetime(raw: dict, attr_name: str) -> datetime | None:
    val = _attr_value(raw, attr_name)
    if val is None:
        return None
    # OpenRemote can return epoch milliseconds (int) or ISO 8601 string
    if isinstance(val, (int, float)):
        return datetime.fromtimestamp(val / 1000, tz=timezone.utc)
    if isinstance(val, str):
        try:
            dt = datetime.fromisoformat(val)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
            return dt
        except ValueError:
            _LOGGER.warning("Cannot parse datetime value: %s", val)
            return None
    return None


class OurGridCoordinator(DataUpdateCoordinator[OurGridData]):
    """Fetches data from both OurGrid assets every 30 seconds."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: OurGridApiClient,
        challenge_asset_id: str,
        meter_asset_id: str,
        config_entry: ConfigEntry,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api
        self._challenge_asset_id = challenge_asset_id
        self._meter_asset_id = meter_asset_id

    async def _async_update_data(self) -> OurGridData:
        try:
            challenge_raw, meter_raw = await asyncio.gather(
                self.api.async_get_asset(self._challenge_asset_id),
                self.api.async_get_asset(self._meter_asset_id),
            )
        except OurGridAuthError as err:
            raise ConfigEntryAuthFailed from err
        except OurGridConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except OurGridApiError as err:
            raise UpdateFailed(f"API error: {err}") from err

        return OurGridData(
            challenge_start=_parse_datetime(challenge_raw, ATTR_CHALLENGE_START),
            challenge_end=_parse_datetime(challenge_raw, ATTR_CHALLENGE_END),
            challenge_points_exchange_rate=_parse_float(
                challenge_raw, ATTR_CHALLENGE_POINTS_EXCHANGE_RATE
            ),
            challenge_status=_attr_value(meter_raw, ATTR_CHALLENGE_STATUS),
            challenge_power_limit=_parse_float(meter_raw, ATTR_CHALLENGE_POWER_LIMIT),
            power=_parse_float(meter_raw, ATTR_POWER),
            challenge_earnings=_parse_float(meter_raw, ATTR_CHALLENGE_EARNINGS),
            challenges_joined=_parse_float(meter_raw, ATTR_CHALLENGES_JOINED),
            total_points=_parse_float(meter_raw, ATTR_TOTAL_POINTS),
            challenge_points_current=_parse_float(meter_raw, ATTR_CHALLENGE_POINTS_CURRENT),
            challenge_points=_parse_float(meter_raw, ATTR_CHALLENGE_POINTS),
            peak_points=_parse_float(meter_raw, ATTR_PEAK_POINTS),
            connection_quality=_parse_float(meter_raw, ATTR_CONNECTION_QUALITY),
            connection_status=_attr_value(meter_raw, ATTR_CONNECTION_STATUS),
            wifi_signal=_parse_float(meter_raw, ATTR_WIFI_SIGNAL),
        )
