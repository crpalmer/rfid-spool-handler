from rfid import Reader as RFIDReader
from bambu import BambuMQTT
from machine import Pin
from neopixel import NeoPixel
import _thread
import time
from wifi import wifi_connect

wifi_connect()

lock = _thread.allocate_lock()
spool = None
spool_timeout = -1
new_spool_active_ms = 5*60*1000

class MQTT(BambuMQTT):
    def on_tray_change(self, ams_id, old_tray, new_tray):
        global spool
        
        print(f"ams {ams_id} changed {old_tray} -> {new_tray}")
        if old_tray.is_empty() and not new_tray.is_empty():
            lock.acquire()
            if spool != None and time.ticks_ms() <= spool_timeout:
                print(f"Loading new spool information: {spool}")
                spool = None
                next_light_update = 0		# technically not thread safe but should be okay
            lock.release()

def rfid_reader():
    global spool
    global spool_timeout
    global next_light_update
    rfid_reader = RFIDReader(Pin(0), Pin(1))
    
    while True:
        new_spool = None
        while not new_spool:
            new_spool = rfid_reader.get_tag_blocking()
        while rfid_reader.is_present(100):
            pass
        lock.acquire()
        spool = new_spool
        spool_timeout = time.ticks_ms() + new_spool_active_ms
        lock.release()
        next_light_update = 0		# technically not thread safe but should be okay
        print(f"queued new spool until {spool_timeout}ms: {spool}")

def light_update(light):
    lock.acquire()
    left = spool_timeout - time.ticks_ms() if spool is not None else 0
    lock.release()
    
    if left <= 0:
        light[0] = (0x10, 0x10, 0x10)
    else:
        light[0] = (0x00, int((25 * left / new_spool_active_ms) + 1), 0)
    light.write()

_thread.start_new_thread(rfid_reader, ())

light = NeoPixel(Pin(2), 1)
mqtt = MQTT("192.168.1.22", serial="0948AD561200005", access_code="75875fca")
next_light_update = 0
while True:
    if time.ticks_ms() > next_light_update:
        next_light_update = time.ticks_ms() + 1000
        light_update(light)
    mqtt.poll()
    time.sleep_ms(10)