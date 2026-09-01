from rfid import Reader as RFIDReader
from bambu import BambuMQTT
from machine import Pin
import _thread
import time

class MQTT(BambuMQTT):
    def on_tray_change(self, ams_id, old_tray, new_tray):
        print(f"ams {ams_id} changed {old_tray} -> {new_tray}")
        if old_tray.is_empty() and not new_tray.is_empty():
            lock.acquire()
            if spool != None and time.ticks_ms() <= spool_timeout:
                print(f"Loading new spool information: {spool}")
            lock.release()

lock = _thread.allocate_lock()
spool = None
spool_timeout = -1

def rfid_reader():
    global spool
    global spool_timeout
    
    rfid_reader = RFIDReader(Pin(0), Pin(1))
    
    while True:
        new_spool = None
        while not new_spool:
            new_spool = rfid_reader.get_tag_blocking()
        while rfid_reader.is_present(100):
            pass
        lock.acquire()
        spool = new_spool
        spool_timeout = time.ticks_ms() + 5*60*1000
        lock.release()
        print(f"queued new spool until {spool_timeout}ms: {spool}")
        
_thread.start_new_thread(rfid_reader, ())

mqtt = MQTT("192.168.1.22", serial="0948AD561200005", access_code="75875fca")
mqtt.run()