from machine import UART, Pin
import time
from pn532.uart import PN532_UART as PN532
import json

uart = UART(0, tx=Pin(0), rx=Pin(1), baudrate=115200)
reset = Pin(2, Pin.OUT)
pn = PN532(uart) #, reset=reset)

class Record:
    def __init__(self, pn):
        data = bytearray()
        block_num = 4
        while True:
            block = pn.ntag2xx_read_block(block_num)
            if block is None:
                break
            data += block
            block_num += 1
            done = False

        print("type " + str(data[0]) + " len " + str(data[1]))
        record = data[2:(2+data[1])]
        tnf = record[0] & 0x07
        type_len = record[1]
        payload_len = record[2]
        idx = 4 if record[0] & 0x08 else 3
        type = record[idx:(idx+type_len)]
        payload = record[(idx+type_len):(idx+type_len+payload_len)]
        parsed = json.loads(payload)
        print(parsed)
        
while True:
    while not pn.read_passive_target(timeout=30000):
        print("waiting")
        
    while True:
        try:
            Record(pn)
            break
        except:
            if not pn.read_passive_target(timeout=1000):
                break
            print("retry read")
            
    while pn.read_passive_target(timeout=100):
        print("go away")
        time.sleep(0.1)
