from rfid import Reader as RFIDReader
from bambu import BambuMQTT
from machine import Pin
from neopixel import NeoPixel
import time
from wifi import wifi_connect

new_spool_active_ms = 5*60*1000

print("trying to connect to wifi")
wifi_connect()

class GlobalState:
    def __init__(self):
        self.spool = None
        self.spool_timeout = -1
        self.new_spool_active_ms = 5*60*1000
        self.send_to_ams_id = -1
        self.send_to_tray_id = -1
        self.next_light_update_at = time.ticks_ms()

    def spool_is_sendable(self):
        return self.spool != None and time.ticks_ms() <= self.spool_timeout and self.send_to_ams_id < 0

    def schedule_send_spool(self, ams_id, tray_id):
        self.send_to_ams_id = ams_id
        self.send_to_tray_id = tray_id
        print(f"scheduled send to ({self.send_to_ams_id}, {self.send_to_tray_id}) for {self.spool}")

    def send_spool_if_ready(self, mqtt):
        if self.send_to_ams_id >= 0 and self.send_to_tray_id >= 0:
            print(f"Loading new spool information: {self.spool}")
            mqtt.send_ams_filament_information(self.send_to_ams_id, self.send_to_tray_id, self.spool)
            self.send_to_ams_id = -1
            self.spool = None
            self.next_light_update_at = time.ticks_ms()
        
    def record_rfid_read(self, spool):
        self.spool = spool
        self.spool_timeout = time.ticks_ms() + new_spool_active_ms
        self.next_light_update_at = time.ticks_ms()
        print(f"queued new spool until {self.spool_timeout}ms: {self.spool}")

    def get_spool_ready_ms(self):
        return self.spool_timeout - time.ticks_ms() if self.spool is not None else 0

    def should_update_lights(self):
        if time.ticks_ms() >= self.next_light_update_at:
            self.next_light_update_at = time.ticks_ms() + 1000
            return True
        return False
    
class MQTT(BambuMQTT):
    def on_tray_change(self, ams_id, old_tray, new_tray):
        print(f"ams {ams_id} changed {old_tray} -> {new_tray}")
        if old_tray.is_empty() and not new_tray.is_empty():
            if global_state.spool_is_sendable():
                global_state.schedule_send_spool(ams_id, new_tray.get_id())

def light_update(light):
    if global_state.should_update_lights():
        left = global_state.get_spool_ready_ms()
        if left <= 0:
            light[0] = (0x10, 0x10, 0x10)
        else:
            light[0] = (0x00, int((25 * left / new_spool_active_ms) + 1), 0)
        light.write()

def main():
    rfid_reader = RFIDReader(Pin(0), Pin(1))
    mqtt = MQTT("192.168.1.22", serial="0948AD561200005", access_code="75875fca")
    light = NeoPixel(Pin(2), 1)
    
    rfid_busy = False
    while True:
        light_update(light)
        
        if rfid_busy:
            rfid_busy = rfid_reader.is_present(100)
        else:
            spool = rfid_reader.poll()
            if spool is not None:
#                 mqtt.send_ams_filament_information(0, 0, spool)
                global_state.record_rfid_read(spool)
                print(mqtt._default_info_idx(spool))
                rfid_busy = True 

        mqtt.poll()
        global_state.send_spool_if_ready(mqtt)

global_state = GlobalState()
main()