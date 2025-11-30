import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import logging
import asyncio

from bleak import BleakScanner, BleakClient
from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class BluetoothDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step 1: scan for devices and let user pick address."""
        errors = {}
        if user_input is not None:
            address = user_input["address"]
            return await self.async_step_service({"address": address})

        # Scan for devices
        devices = await BleakScanner.discover(timeout=5.0)
        choices = {dev.address: f"{dev.name or 'Unknown'} ({dev.address})" for dev in devices}

        schema = vol.Schema({
            vol.Required("address"): vol.In(choices)
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_service(self, user_input=None):
        """Step 2: connect to device and list services/characteristics."""
        errors = {}
        address = user_input["address"]

        async with BleakClient(address) as client:
            services = await client.get_services()
            char_map = {}
            for service in services:
                for char in service.characteristics:
                    char_map[char.uuid] = f"{service.uuid} / {char.uuid}"

        schema = vol.Schema({
            vol.Required("char_uuid"): vol.In(char_map),
            vol.Optional("update_interval", default=DEFAULT_UPDATE_INTERVAL): int,
        })

        if "char_uuid" in user_input:
            return self.async_create_entry(
                title=f"BLE {address}",
                data={
                    "address": address,
                    "char_uuid": user_input["char_uuid"],
                    "update_interval": user_input.get("update_interval", DEFAULT_UPDATE_INTERVAL),
                },
            )

        return self.async_show_form(step_id="service", data_schema=schema, errors=errors)
