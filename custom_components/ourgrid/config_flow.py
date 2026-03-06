"""Config flow for the OurGrid integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OurGridApiClient, OurGridAuthError, OurGridApiError, OurGridConnectionError
from .const import (
    CONF_CHALLENGE_ASSET_ID,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_METER_ASSET_ID,
    CONF_REALM,
    DOMAIN,
)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_REALM): str,
        vol.Required(CONF_CLIENT_ID): str,
        vol.Required(CONF_CLIENT_SECRET): str,
        vol.Required(CONF_CHALLENGE_ASSET_ID): str,
        vol.Required(CONF_METER_ASSET_ID): str,
    }
)


class OurGridConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OurGrid."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_REALM]}_{user_input[CONF_CLIENT_ID]}"
            )
            self._abort_if_unique_id_configured()

            try:
                await self._validate_input(user_input)
            except OurGridAuthError:
                errors["base"] = "invalid_auth"
            except OurGridConnectionError:
                errors["base"] = "cannot_connect"
            except OurGridApiError:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"OurGrid ({user_input[CONF_REALM]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def _validate_input(self, user_input: dict[str, Any]) -> None:
        session = async_get_clientsession(self.hass)
        client = OurGridApiClient(
            session=session,
            realm=user_input[CONF_REALM],
            client_id=user_input[CONF_CLIENT_ID],
            client_secret=user_input[CONF_CLIENT_SECRET],
        )
        await client.async_test_connection(user_input[CONF_CHALLENGE_ASSET_ID])

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of an existing entry."""
        reconfigure_entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_REALM]}_{user_input[CONF_CLIENT_ID]}"
            )
            self._abort_if_unique_id_configured(updates=user_input)
            try:
                await self._validate_input(user_input)
            except OurGridAuthError:
                errors["base"] = "invalid_auth"
            except OurGridConnectionError:
                errors["base"] = "cannot_connect"
            except OurGridApiError:
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    title=f"OurGrid ({user_input[CONF_REALM]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_REALM, default=reconfigure_entry.data.get(CONF_REALM, "")): str,
                    vol.Required(CONF_CLIENT_ID, default=reconfigure_entry.data.get(CONF_CLIENT_ID, "")): str,
                    vol.Required(CONF_CLIENT_SECRET): str,
                    vol.Required(CONF_CHALLENGE_ASSET_ID, default=reconfigure_entry.data.get(CONF_CHALLENGE_ASSET_ID, "")): str,
                    vol.Required(CONF_METER_ASSET_ID, default=reconfigure_entry.data.get(CONF_METER_ASSET_ID, "")): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Handle re-authentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            merged = {**reauth_entry.data, **user_input}
            try:
                await self._validate_input(merged)
            except OurGridAuthError:
                errors["base"] = "invalid_auth"
            except OurGridConnectionError:
                errors["base"] = "cannot_connect"
            except OurGridApiError:
                errors["base"] = "unknown"
            else:
                self.hass.config_entries.async_update_entry(
                    reauth_entry, data=merged
                )
                await self.hass.config_entries.async_reload(reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CLIENT_ID, default=reauth_entry.data.get(CONF_CLIENT_ID, "")): str,
                    vol.Required(CONF_CLIENT_SECRET): str,
                }
            ),
            errors=errors,
        )
