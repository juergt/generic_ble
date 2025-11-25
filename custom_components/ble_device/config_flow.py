import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import logging
import asyncio

from bleak import BleakClient
from .const import DOMAIN, DEFAULT_PIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required("address"): str,
    vol.Optional("pin", default=DEFAULT_PIN): str,
    vol.Optional("char_uuid", default="YOUR_CHAR_UUID"): str,
    vol.Optional("update_interval", default=30): int,
})

class BleDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            address = user_input["address"]
            pin = user_input.get("pin")

            # Try to pair/connect to validate
            try:
                client = BleakClient(address)
                paired = await client.pair(protection_level=2)
                if not paired:
                    errors["base"] = "pair_failed"
                else:
                    await client.connect()
                    await client.disconnect()
                    return self.async_create_entry(
                        title=f"BLE Device {address}", data=user_input
                    )
            except Exception as e:
                _LOGGER.error("Validation failed: %s", e)
                errors["base"] = "cannot