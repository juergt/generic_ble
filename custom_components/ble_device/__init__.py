import logging
from bleak import BleakClient
from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import async_load_platform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    address = entry.data["address"]
    char_uuid = entry.data["char_uuid"]
    update_interval = entry.data.get("update_interval")

    client = BleakClient(address)

    try:
        await client.connect()
        _LOGGER.info("Connected to BLE device %s", address)
        hass.data[DOMAIN] = client
    except Exception as e:
        _LOGGER.error("BLE connection failed: %s", e)
        return False

    async def handle_write(call):
        value = call.data["value"]
        await client.write_gatt_char(char_uuid, bytes([value]))
        _LOGGER.info("Wrote %s to %s", value, char_uuid)

    hass.services.async_register(DOMAIN, "write_value", handle_write)

    hass.async_create_task(
        async_load_platform(hass, "sensor", DOMAIN, {"char_uuid": char_uuid, "update_interval": update_interval}, entry)
    )

    return True
