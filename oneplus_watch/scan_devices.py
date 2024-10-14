import asyncio
from bleak import BleakScanner

async def scan_devices():
    devices = await BleakScanner.discover()
    for device in devices:
        print(device)

loop = asyncio.get_event_loop()
loop.run_until_complete(scan_devices())
