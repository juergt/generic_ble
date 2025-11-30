from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import logging
from bleak import BleakClient
from bleak_retry_connector import establish_connection
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    address = data["address"]
    char_configs = data["char_configs"]
    update_interval = entry.data.get("update_interval", 30)

    sensors = []
    for cfg in char_configs:
        uuid = cfg["uuid"]
        fmt = cfg.get("format", "hex")

        async def read_ble_value(uuid=uuid, fmt=fmt):
            try:
                # Ensure connection
                if not client.is_connected:
                    _LOGGER.warning("Client disconnected, re-establishing before read...")
                    new_client = await establish_connection(BleakClient(address), address, timeout=20.0, max_attempts=5)
                    hass.data[DOMAIN][entry.entry_id]["client"] = new_client
                    client = new_client

                raw = await client.read_gatt_char(uuid)
                if fmt == "int":
                    return int.from_bytes(raw, byteorder="little")
                elif fmt == "string":
                    return raw.decode("utf-8", errors="ignore")
                else:
                    return raw.hex()
            except Exception as e:
                raise UpdateFailed(f"BLE read failed: {e}")

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"ble_{uuid}",
            update_method=read_ble_value,
            update_interval=update_interval,
        )
        await coordinator.async_refresh()
        sensors.append(BleSensor(coordinator, uuid, fmt))

    async_add_entities(sensors)

class BleSensor(SensorEntity):
    def __init__(self, coordinator, uuid, fmt):
        self._coordinator = coordinator
        self._uuid = uuid
        self._fmt = fmt
        self._attr_name = f"BLE {uuid} ({fmt})"
        self._attr_unique_id = f"bluetooth_device_{uuid}_{fmt}"

    @property
    def native_value(self):
        return self._coordinator.data

    async def async_update(self):
        await self._coordinator.async_request_refresh()
