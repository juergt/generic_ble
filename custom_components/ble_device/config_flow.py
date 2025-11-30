import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL

DATA_SCHEMA = vol.Schema({
    vol.Required("address"): str,
    vol.Required("service_uuid"): str,
    vol.Required("char_uuid"): str,
    vol.Optional("update_interval", default=DEFAULT_UPDATE_INTERVAL): int,
})

class BluetoothDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Basic validation: just ensure fields are present
            return self.async_create_entry(title=f"BLE {user_input['address']}", data=user_input)

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)
