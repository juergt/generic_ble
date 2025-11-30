from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    char_uuid = data["char_uuid"]
    update_interval = entry.data.get("update_interval", 30)

    async def read_ble_value():
        try:
            data = await client.read_gatt_char(char_uuid)
            return data.hex()  # return hex string by default
        except Exception as e:
            raise UpdateFailed(f"BLE read failed: {e}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="bluetooth_device",
        update_method=read_ble_value,
        update_interval=update_interval,
    )

    await coordinator.async_refresh()
    async_add_entities([BleSensor(coordinator, char_uuid)])

class BleSensor(SensorEntity):
    def __init__(self, coordinator, char_uuid):
        self._coordinator = coordinator
        self._char_uuid = char_uuid
        self._attr_name = f"BLE {char_uuid}"
        self._attr_unique_id = f"bluetooth_device_{char_uuid}"

    @property
    def native_value(self):
        return self._coordinator.data

    async def async_update(self):
        await self._coordinator.async_request_refresh()
