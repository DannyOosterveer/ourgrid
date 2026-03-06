"""Shared base entity for the OurGrid integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OurGridCoordinator


class OurGridEntity(CoordinatorEntity[OurGridCoordinator]):
    """Base class for all OurGrid entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OurGridCoordinator,
        description: EntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="OurGrid",
            manufacturer="OurGrid",
            model="Grid Congestion App",
            entry_type=DeviceEntryType.SERVICE,
        )
