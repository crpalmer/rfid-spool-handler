from rfid import Reader as RFIDReader
from machine import Pin
import time

rfid_reader = RFIDReader(Pin(0), Pin(1))
spool = None

while True:
    if spool is None:
        spool = rfid_reader.poll()
        if spool is not None:
            print(spool)
    else:
        if not rfid_reader.is_present():
            spool = None
            print("it went away")