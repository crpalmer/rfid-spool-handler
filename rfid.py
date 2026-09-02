from machine import UART, Pin
from pn532.uart import PN532_UART as PN532
import json
import time

class Reader:
    def __init__(self, tx, rx):
        self._uart = UART(0, tx=tx, rx=rx, baudrate=115200)
        self._pn = PN532(self._uart, debug=False) #, reset=reset)

    def is_present(self, timeout=100):
        try:
            return self._pn.read_passive_target(timeout=timeout) is not None
        except Exception as e:
            print(f"RFID is present test failed: {e}")
            return False

    def poll(self):
        if (self.is_present()):
            return self._read_tag()
        return None
    
    def get_tag_blocking(self):
        while True:
            while not self.is_present(30000):
                pass
            tag = self._read_tag()
            if tag != None:
                return tag

    def _read_tag(self):
        try:
            data = bytearray()
            block_num = 4
            while True:
                block = self._pn.ntag2xx_read_block(block_num)
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