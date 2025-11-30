import logging
from bleak import BleakClient
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    address = entry.data["address"]
    char_uuid = entry.data["char_uuid"]

    client = BleakClient(address)

    try:
        await client.connect()
        _LOGGER.info("Connected to BLE device %s", address)
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
            "client": client,
            "char_uuid": char_uuid,
        }
    except Exception as e:
        _LOGGER.error("BLE connection failed: %s", e)
        return False

    # Forward to sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    # Register service
    async def handle_write(call):
        value = call.data["value"]
        fmt = call.data.get("format", "string")
        if fmt == "int":
            payload = bytes([int(value)])
        elif fmt == "hex":
            payload = bytes.fromhex(value.replace(" ", ""))
        else:
            payload = value.encode("utf-8")
        await client.write_gatt_char(char_uuid, payload)

    hass.services.async_register(DOMAIN, "write_value", handle_write)

    return True
