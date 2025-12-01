import asyncio
import logging
from bleak import BleakClient
from bleak_retry_connector import establish_connection

_LOGGER = logging.getLogger(__name__)

async def reconnect_with_backoff(address, max_attempts=5, base_delay=2):
    attempt = 0
    while attempt < max_attempts:
        try:
            client = await establish_connection(
                BleakClient(address),
                address,
                timeout=20.0,
                max_attempts=1
            )
            _LOGGER.info("Reconnected to BLE device %s on attempt %d", address, attempt + 1)
            return client
        except Exception as e:
            delay = base_delay * (2 ** attempt)
            _LOGGER.warning("Reconnect attempt %d failed: %s. Retrying in %ds", attempt + 1, e, delay)
            await asyncio.sleep(delay)
            attempt += 1
    raise RuntimeError(f"Failed to reconnect to {address} after {max_attempts} attempts")
