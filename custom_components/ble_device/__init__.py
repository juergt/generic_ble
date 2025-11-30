async def async_setup_entry(hass, entry):
    address = entry.data["address"]
    char_configs = entry.data["char_configs"]

    client = BleakClient(address)
    await client.connect()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "char_configs": char_configs,
    }

    # Forward to sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    # Register service
    async def handle_write(call):
        char_uuid = call.data["char_uuid"]
        value = call.data["value"]
        fmt = call.data.get("format", "string")

        if fmt == "int":
            payload = bytes([int(value)])
        elif fmt == "hex":
            payload = bytes.fromhex(value.replace(" ", ""))
        else:
            payload = value.encode("utf-8")

        await client.write_gatt_char(char_uuid, payload)
        _LOGGER.info("Wrote %s (%s) to %s", value, fmt, char_uuid)

    hass.services.async_register(DOMAIN, "write_value", handle_write)

    return True
