import logging
from bleak import BleakClient
from bleak_retry_connector import establish_connection
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .backoff import reconnect_with_backoff

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    address = entry.data["address"]
    char_configs = entry.data["char_configs"]

    client = await establish_connection(
        BleakClient(address),
        address,
        timeout=20.0,
        max_attempts=5
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "address": address,
        "char_configs": char_configs,
    }

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    async def handle_write(call):
        char_uuid = call.data["char_uuid"]
        value = call.data["value"]
        fmt = call.data.get("format")

        if fmt is None:
            raise ValueError("You must specify 'format' (int, string, hex) in the service call")

        client = hass.data[DOMAIN][entry.entry_id]["client"]
        if not client.is_connected:
            _LOGGER.warning("Client disconnected, trying backoff reconnect before write...")
            client = await reconnect_with_backoff(address)
            hass.data[DOMAIN][entry.entry_id]["client"] = client

        if fmt == "int":
            payload = bytes([int(value)])
        elif fmt == "hex":
            payload = bytes.fromhex(value.replace(" ", ""))
        elif fmt == "string":
            payload = value.encode("utf-8")
        else:
            raise ValueError(f"Unsupported format: {fmt}")

        await client.write_gatt_char(char_uuid, payload)
        _LOGGER.info("Wrote %s (%s) to %s", value, fmt, char_uuid)

    hass.services.async_register(DOMAIN, "write_value", handle_write)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    data = hass.data[DOMAIN].pop(entry.entry_id, None)
    if data:
        client: BleakClient = data["client"]
        try:
            if client.is_connected:
                await client.disconnect()
                _LOGGER.info("Disconnected BLE client %s", entry.data["address"])
        except Exception as e:
            _LOGGER.warning("Error disconnecting BLE client: %s", e)

    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return unload_ok
