from machine import Pin
from neopixel import NeoPixel
import asyncio
import time

from controller import controller
from rfid import RFIDReader
from webserver import web_server_start

async def light_task(light):
    last_value = (-1, -1, -1)
    while True:
        if controller.get_spool_to_send().is_ready():
            light[0] = (0x00, 0x20, 0)
        else:
            light[0] = (0x10, 0x10, 0x10)
        if last_value != light[0]:
            light.write()
            last_value = light[0]
        await asyncio.sleep_ms(100)

async def main():
    asyncio.create_task(controller.run())
    asyncio.create_task(light_task(NeoPixel(Pin(2), 1)))
    web_server_start()

    try:
        rfid_reader = RFIDReader(Pin(0), Pin(1))
        rfid_reader.run()
    except Exception as e:
        print(f"Failed to find RFID reader: {e}\nNO RFIDS WILL BE SCANNED DURING THIS RUN")
        controller.set_rfid_error(str(e))

    while True:
        await asyncio.sleep(1000)

asyncio.run(main())
