import asyncio
from bleak import BleakClient

# Replace this with the Bluetooth address of your OnePlus Watch
WATCH_ADDRESS = "5C:17:CF:8D:12:1B"

# Likely UUID for heart rate notifications based on the previous scan
NOTIFY_CHARACTERISTIC_UUID = "d44bc439-abfd-45a2-b575-925416129600"

# Callback function to handle notifications
def notification_handler(sender, data):
    print(f"Notification from {sender}: {data}")
    # You can parse 'data' here based on the expected format

async def connect_and_get_notifications():
    async with BleakClient(WATCH_ADDRESS, use_cached=False, pairing=False) as client:
        # Ensure connection
        if client.is_connected:
            print("Connected to OnePlus Watch")

            # Start receiving notifications
            try:
                await client.start_notify(NOTIFY_CHARACTERISTIC_UUID, notification_handler)

                # Keep the connection alive and receiving data for 60 seconds
                await asyncio.sleep(60)

                # Stop notifications after 60 seconds (or other desired duration)
                await client.stop_notify(NOTIFY_CHARACTERISTIC_UUID)

            except Exception as e:
                print(f"Error: {e}")

# Run the async function to connect to the watch
loop = asyncio.get_event_loop()
loop.run_until_complete(connect_and_get_notifications())
