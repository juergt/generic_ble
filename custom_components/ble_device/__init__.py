async def async_setup_entry(hass: HomeAssistant, entry):
    address = entry.data["address"]
    char_uuid = entry.data["char_uuid"]

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
        fmt = call.data.get("format", "string")

        if fmt == "int":
            payload = bytes([int(value)])
        elif fmt == "hex":
            # Accept hex string like "0A FF 1B"
            payload = bytes.fromhex(value.replace(" ", ""))
        else:  # default string
            payload = value.encode("utf-8")

        await client.write_gatt_char(char_uuid, payload)
        _LOGGER.info("Wrote %s (%s) to %s", value, fmt, char_uuid)

    hass.services.async_register(DOMAIN, "write_value", handle_write)

    # Load sensor platform
    hass.async_create_task(
        async_load_platform(hass, "sensor", DOMAIN, {"char_uuid": char_uuid}, entry)
    )

    return True
