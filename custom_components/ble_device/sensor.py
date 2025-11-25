from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    client = hass.data["ble_device"]
    char_uuid = discovery_info["char_uuid"]
    update_interval = discovery_info.get("update_interval", 30)

    async def read_ble_value():
        try:
            data = await client.read_gatt_char(char_uuid)
            return int.from_bytes(data, byteorder="little")
        except Exception as e:
            raise UpdateFailed(f"BLE read failed: {e}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="ble_device",
        update_method=read_ble_value,
        update_interval=update_interval,
    )

    await coordinator.async_refresh()
    async_add_entities([BleSensor(coordinator, char_uuid)])

class BleSensor(SensorEntity):
    def __init__(self, coordinator, char_uuid):
        self._coordinator = coordinator
        self._char_uuid = char_uuid
        self._attr_name = "BLE Value"
        self._attr_unique_id = f"ble_device_{char_uuid}"

    @property
    def native_value(self):
        return self._coordinator.data

    async def async_update(self):
        await self._coordinator.async_request_refresh()
