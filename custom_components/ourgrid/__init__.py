"""OurGrid Home Assistant integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OurGridApiClient
from .const import (
    CONF_CHALLENGE_ASSET_ID,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_METER_ASSET_ID,
    CONF_REALM,
)
from .coordinator import OurGridCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]

type OurGridConfigEntry = ConfigEntry[OurGridCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: OurGridConfigEntry) -> bool:
    """Set up OurGrid from a config entry."""
    session = async_get_clientsession(hass)
    api = OurGridApiClient(
        session=session,
        realm=entry.data[CONF_REALM],
        client_id=entry.data[CONF_CLIENT_ID],
        client_secret=entry.data[CONF_CLIENT_SECRET],
    )
    coordinator = OurGridCoordinator(
        hass=hass,
        api=api,
        challenge_asset_id=entry.data[CONF_CHALLENGE_ASSET_ID],
        meter_asset_id=entry.data[CONF_METER_ASSET_ID],
        config_entry=entry,
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: OurGridConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
