import voluptuous as vol
from homeassistant import config_entries
from bleak import BleakScanner, BleakClient
from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL

class BluetoothDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            address = user_input["address"]
            return await self.async_step_service({"address": address})

        devices = await BleakScanner.discover(timeout=5.0)
        choices = {dev.address: f"{dev.name or 'Unknown'} ({dev.address})" for dev in devices}

        schema = vol.Schema({vol.Required("address"): vol.In(choices)})
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_service(self, user_input=None):
        address = user_input["address"]

        async with BleakClient(address) as client:
            services = await client.get_services()
            char_map = {}
            for service in services:
                for char in service.characteristics:
                    char_map[char.uuid] = f"{service.uuid} / {char.uuid}"

        # Let user select multiple characteristics and formats
        schema = vol.Schema({
            vol.Required("char_configs", default=[]): vol.All(
                vol.Schema([
                    {
                        vol.Required("uuid"): vol.In(char_map),
                        vol.Optional("format", default="hex"): vol.In(["int", "string", "hex"])
                    }
                ])
            ),
            vol.Optional("update_interval", default=DEFAULT_UPDATE_INTERVAL): int,
        })

        if "char_configs" in user_input:
            return self.async_create_entry(
                title=f"BLE {address}",
                data={
                    "address": address,
                    "char_configs": user_input["char_configs"],
                    "update_interval": user_input.get