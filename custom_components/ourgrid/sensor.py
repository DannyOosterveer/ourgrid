"""Sensor entities for the OurGrid integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import OurGridCoordinator, OurGridData
from .entity import OurGridEntity


@dataclass(frozen=True, kw_only=True)
class OurGridSensorEntityDescription(SensorEntityDescription):
    """Describes an OurGrid sensor, extended with a value accessor."""

    value_fn: Callable[[OurGridData], StateType | datetime] = lambda _: None


SENSOR_DESCRIPTIONS: tuple[OurGridSensorEntityDescription, ...] = (
    OurGridSensorEntityDescription(
        key="challenge_start",
        translation_key="challenge_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.challenge_start,
    ),
    OurGridSensorEntityDescription(
        key="challenge_end",
        translation_key="challenge_end",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.challenge_end,
    ),
    OurGridSensorEntityDescription(
        key="challenge_points_exchange_rate",
        translation_key="challenge_points_exchange_rate",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement="EUR",
        suggested_display_precision=4,
        value_fn=lambda data: data.challenge_points_exchange_rate,
    ),
    OurGridSensorEntityDescription(
        key="challenge_power_limit",
        translation_key="challenge_power_limit",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.challenge_power_limit,
    ),
    OurGridSensorEntityDescription(
        key="power",
        translation_key="power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.power,
    ),
    # Points & earnings
    OurGridSensorEntityDescription(
        key="challenge_earnings",
        translation_key="challenge_earnings",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement="EUR",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.challenge_earnings,
    ),
    OurGridSensorEntityDescription(
        key="challenges_joined",
        translation_key="challenges_joined",
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
        value_fn=lambda data: data.challenges_joined,
    ),
    OurGridSensorEntityDescription(
        key="total_points",
        translation_key="total_points",
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
        value_fn=lambda data: data.total_points,
    ),
    OurGridSensorEntityDescription(
        key="challenge_points_current",
        translation_key="challenge_points_current",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.challenge_points_current,
    ),
    OurGridSensorEntityDescription(
        key="challenge_points",
        translation_key="challenge_points",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.challenge_points,
    ),
    OurGridSensorEntityDescription(
        key="peak_points",
        translation_key="peak_points",
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
        value_fn=lambda data: data.peak_points,
    ),
    # Connectivity (diagnostic)
    OurGridSensorEntityDescription(
        key="connection_quality",
        translation_key="connection_quality",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.connection_quality,
    ),
    OurGridSensorEntityDescription(
        key="wifi_signal",
        translation_key="wifi_signal",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.wifi_signal,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OurGrid sensors from a config entry."""
    coordinator: OurGridCoordinator = entry.runtime_data
    async_add_entities(
        OurGridSensorEntity(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class OurGridSensorEntity(OurGridEntity, SensorEntity):
    """A single OurGrid sensor."""

    entity_description: OurGridSensorEntityDescription

    @property
    def native_value(self) -> StateType | datetime:
        return self.entity_description.value_fn(self.coordinator.data)
