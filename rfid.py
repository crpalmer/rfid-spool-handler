from machine import UART, Pin
from pn532.uart import PN532_UART as PN532
import asyncio
import json
import time

from controller import controller

class RFIDReader:
    def __init__(self, tx, rx):
        self._uart = UART(0, tx=tx, rx=rx, baudrate=115200)
        self._pn = PN532(self._uart, debug=False) #, reset=reset)

    def run(self):
        asyncio.create_task(self.rfid_reader_task())

    async def is_present_async(self, timeout=100):
        try:
            return await self._pn.read_passive_target_async(timeout=timeout) is not None
        except Exception as e:
            print(f"RFID is present test failed: {e}")
            return False

    async def get_tag_blocking_async(self):
        while True:
            while not await self.is_present(30000):
                pass
            tag = await self._read_tag_async()
            if tag != None:
                return tag

    async def read_tag_async(self):
        try:
            data = bytearray()
            block_num = 4
            while True:
                block = await self._pn.ntag2xx_read_block_async(block_num)
                if block is None:
                    break
                data += block
                block_num += 1
                done = False

            record = data[2:(2+data[1])]
            tnf = record[0] & 0x07
            type_len = record[1]
            payload_len = record[2]
            
            idx = 4 if record[0] & 0x08 else 3
            type = record[idx:(idx+type_len)]
            payload = record[(idx+type_len):(idx+type_len+payload_len)]
            parsed = json.loads(payload)
            return parsed
        except Exception as e:
            print("Failed to process rfid payload: " + str(e))
            return None

    async def rfid_reader_task(self):
        rfid_busy = False
        while True:
            if rfid_busy:
                rfid_busy = await self.is_present_async(30000)
            elif await self.is_present_async(30000):
                print("is_present!")
                spool = await self.read_tag_async()
                if spool is not None:
                    controller.record_rfid_read(spool)
                    rfid_busy = True
