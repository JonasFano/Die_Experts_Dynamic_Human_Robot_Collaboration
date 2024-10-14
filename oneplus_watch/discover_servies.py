import asyncio
from bleak import BleakClient

# Replace with your watch's Bluetooth address
WATCH_ADDRESS = "5C:17:CF:8D:12:1B"

async def discover_services():
    async with BleakClient(WATCH_ADDRESS) as client:
        if client.is_connected:
            print("Connected to OnePlus Watch")
            
            # Get and print all services and characteristics
            services = await client.get_services()
            for service in services:
                print(f"Service: {service.uuid}")
                for characteristic in service.characteristics:
                    print(f"  Characteristic: {characteristic.uuid}, Properties: {characteristic.properties}")

# Run the async function to connect and discover services
loop = asyncio.get_event_loop()
loop.run_until_complete(discover_services())


"""
Connected to OnePlus Watch
/home/jonas/Downloads/Die_Experts_Dynamic_Human_Robot_Collaboration/oneplus_watch/discover_servies.py:13: FutureWarning: This method will be removed future version, use the services property instead.
  services = await client.get_services()
Service: 0000fee9-0000-1000-8000-00805f9b34fb
  Characteristic: d44bc439-abfd-45a2-b575-925416129600, Properties: ['read', 'write-without-response', 'write', 'notify']
  Characteristic: d44bc439-abfd-45a2-b575-925416129601, Properties: ['read', 'write-without-response', 'write', 'notify']
Service: 00003802-0000-1000-8000-00805f9b34fb
  Characteristic: 00004a02-0000-1000-8000-00805f9b34fb, Properties: ['read', 'write', 'notify']
Service: 00002760-08c2-11e1-9073-0e8ac72e1012
  Characteristic: 00002760-08c2-11e1-9073-0e8ac72e0014, Properties: ['read', 'write-without-response', 'write', 'notify']
  Characteristic: 00002760-08c2-11e1-9073-0e8ac72e0015, Properties: ['read', 'write-without-response', 'write', 'notify']
Service: 00006a02-0000-1000-8000-00805f9b34fb
  Characteristic: 00006b02-0000-1000-8000-00805f9b34fb, Properties: ['read', 'write-without-response', 'write', 'notify']
Service: 00002760-08c2-11e1-9073-0e8ac72e1011
  Characteristic: 00002760-08c2-11e1-9073-0e8ac72e0012, Properties: ['read', 'write-without-response', 'write', 'notify']
  Characteristic: 00002760-08c2-11e1-9073-0e8ac72e0013, Properties: ['read', 'write-without-response', 'write', 'notify']
  Characteristic: 00002760-08c2-11e1-9073-0e8ac72e0011, Properties: ['read', 'write-without-response', 'write', 'notify']
Service: 00001801-0000-1000-8000-00805f9b34fb
Service: 1b7e8251-2877-41c3-b46e-cf057c562023
  Characteristic: 8ac32d3f-5cb9-4d44-bec2-ee689169f626, Properties: ['read', 'write-without-response', 'write', 'notify', 'indicate']
Service: 0000180a-0000-1000-8000-00805f9b34fb
  Characteristic: 00002a24-0000-1000-8000-00805f9b34fb, Properties: ['read']
  Characteristic: 00002a29-0000-1000-8000-00805f9b34fb, Properties: ['read']
  Characteristic: 00002a28-0000-1000-8000-00805f9b34fb, Properties: ['read']
  Characteristic: 00002a26-0000-1000-8000-00805f9b34fb, Properties: ['read']
  """