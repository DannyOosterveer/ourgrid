"""Binary sensor entity for the OurGrid integration."""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import OurGridCoordinator, OurGridData
from .entity import OurGridEntity


@dataclass(frozen=True, kw_only=True)
class OurGridBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes an OurGrid binary sensor, extended with a value accessor."""

    value_fn: Callable[[OurGridData], bool | None] = lambda _: None


BINARY_SENSOR_DESCRIPTIONS: tuple[OurGridBinarySensorEntityDescription, ...] = (
    OurGridBinarySensorEntityDescription(
        key="challenge_status",
        translation_key="challenge_status",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda data: None if data.challenge_status is None
        else data.challenge_status == "joinChallenge",
    ),
    OurGridBinarySensorEntityDescription(
        key="connection_status",
        translation_key="connection_status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: None if data.connection_status is None
        else data.connection_status == "connected",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OurGrid binary sensors from a config entry."""
    coordinator: OurGridCoordinator = entry.runtime_data
    async_add_entities(
        OurGridBinarySensorEntity(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class OurGridBinarySensorEntity(OurGridEntity, BinarySensorEntity):
    """An OurGrid binary sensor."""

    entity_description: OurGridBinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.coordinator.data)
