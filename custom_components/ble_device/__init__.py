import logging
from bleak import BleakClient
from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import async_load_platform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    address = entry.data["address"]
    pin = entry.data.get("pin")
    char_uuid = entry.data.get("char_uuid")
    update_interval = entry.data.get("update_interval", 30)

    client = BleakClient(address)

    try:
        # Attempt pairing with PIN
        paired = await client.pair(protection_level=2)
        if not paired:
            _LOGGER.warning("Pairing may require OS agent with PIN %s", pin)

        await client.connect()
        _LOGGER.info("Connected to BLE device %s", address)
        hass.data[DOMAIN] = client
    except Exception as e:
        _LOGGER.error("BLE connection failed: %s", e)
        return False

    # Register service for writing
    async def handle_write(call):
        value = call.data["value"]
        await client.write_gatt_char(char_uuid, bytes([value]))
        _LOGGER.info("Wrote value %s to BLE device", value)

    hass.services.async_register(DOMAIN, "write_ble_value", handle_write)

    # Load sensor platform with UUID and interval
    hass.async_create_task(
        async_load_platform(hass, "sensor", DOMAIN, {"char_uuid": char_uuid, "update_interval": update_interval}, entry)
    )

    return True
