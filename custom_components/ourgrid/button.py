"""Button entity for joining an OurGrid challenge."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import OurGridApiError, OurGridAuthError
from .const import ATTR_CHALLENGE_JOIN_BUTTON, CONF_METER_ASSET_ID, DOMAIN
from .coordinator import OurGridCoordinator
from .entity import OurGridEntity

BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="challenge_join_button",
    translation_key="challenge_join_button",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OurGrid button from a config entry."""
    coordinator: OurGridCoordinator = entry.runtime_data
    async_add_entities([OurGridJoinButtonEntity(coordinator, BUTTON_DESCRIPTION)])


class OurGridJoinButtonEntity(OurGridEntity, ButtonEntity):
    """Button that sends a join signal to the OurGrid challenge."""

    async def async_press(self) -> None:
        """Accept the active challenge by writing true to challengeJoinButton."""
        meter_asset_id = self.coordinator.config_entry.data[CONF_METER_ASSET_ID]
        try:
            await self.coordinator.api.async_write_attribute(
                asset_id=meter_asset_id,
                attribute_name=ATTR_CHALLENGE_JOIN_BUTTON,
                value=True,
            )
        except OurGridAuthError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="auth_failed",
            ) from err
        except OurGridApiError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="api_error",
            ) from err
