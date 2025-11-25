# BLE Device Integration

Custom HACS component to connect Home Assistant with a BLE device that requires PIN pairing.

## Features
- Connects via [bleak](https://github.com/hbldh/bleak)
- Reads GATT characteristics into sensors
- Writes values via Home Assistant services
- Supports PIN pairing (pair via OS tools, then configure in HA)

## Installation
1. Copy repo into `custom_components/ble_device`
2. Add via HACS as a custom repository
3. Configure in Home Assistant UI (Integration → BLE Device)

## Notes
- PIN pairing must be handled by the OS (e.g. `bluetoothctl` on Linux).
- Once paired, Home Assistant can read/write via this integration.
