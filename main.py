from bambu import BambuMQTT
from rfid import Reader as RFIDReader
from webserver import WebServerNotifier, web_server_start, wifi
from wifi import wifi_create_ap, wifi_connect

from machine import Pin
from neopixel import NeoPixel
import asyncio
import time

new_spool_active_ms = 5*60*1000

class Notifier(WebServerNotifier):
    def __init__(self):
        super().__init__()

    def on_filament_config_changed(self, filament):
        global_state.set_filament(filament)

    def on_printer_config_changed(self, printer):
        global_state.connect(printer)

class GlobalState:
    def __init__(self):
        self.spool = None
        self.spool_timeout = -1
        self.new_spool_active_ms = 5*60*1000
        self.send_to_ams_id = -1
        self.send_to_tray_id = -1
        self.next_light_update_at = time.ticks_ms()
        self.mqtt = MQTT()
        self.mqtt_is_connected = False
        self.notifier = Notifier()
        self.filament = {}
        self.last_filament_id = None

    def set_filament(self, filament):
        self.filament = filament

    def connect(self, printer):
        try:
            print(f"Connecting to MQTT server: {printer["ip"]}")
            self.mqtt.disconnect()
            self.mqtt.connect(ip=printer["ip"], serial=printer["serial"], access_code=printer["ac"])
            self.notifier.mqtt_error = None
            self.mqtt_is_connected = True
        except Exception as e:
            self.notifier.mqtt_error = str(e)
            self.mqtt_is_connected = False
            print(f"failed to connect to {printer["ip"]}: {self.notifier.mqtt_error}")

    def mqtt_poll(self):
        if self.mqtt_is_connected:
            self.mqtt.poll()
            self.send_spool_if_ready()

    def spool_is_sendable(self):
        return self.spool != None and time.ticks_ms() <= self.spool_timeout and self.send_to_ams_id < 0

    def schedule_send_spool(self, ams_id, tray_id):
        self.send_to_ams_id = ams_id
        self.send_to_tray_id = tray_id
        print(f"scheduled send to ({self.send_to_ams_id}, {self.send_to_tray_id}) for {self.spool}")

    def find_filament_id_for_spool(self):
        spool = self.spool
        best = None
        best_quality = -1
        for f in self.filament.values():
            if 'filament_id' in f and f.get('brand') == spool.get('brand') and f.get('type') == spool.get('type'):
                quality = 0
                quality += 1 if f.get('subtype') == spool.get('subtype') else 0
                quality += 2 if f.get('color_hex') == spool.get('color_hex') else 0
                if quality > best_quality:
                    best = f
                    best_quality = quality

        return best['filament_id'] if best is not None else None

    def send_spool_if_ready(self):
        if self.send_to_ams_id >= 0 and self.send_to_tray_id >= 0:
            print(f"Loading new spool information: {self.spool}")
            if "filament_id" not in self.spool:
                best_filament_id = self.find_filament_id_for_spool()
                temp_spool = {}
                temp_spool.update(self.spool)
                temp_spool["filament_id"] = best_filament_id
            self.mqtt.send_ams_filament_information(self.send_to_ams_id, self.send_to_tray_id, temp_spool)
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
        global_state.last_filament_id = new_tray.get_info_idx()
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

async def main():
    web_server_start(global_state.notifier, global_state)
    try:
        rfid_reader = RFIDReader(Pin(0), Pin(1))
    except:
        rfid_reader = None
    light = NeoPixel(Pin(2), 1)
    
    rfid_busy = False
    while True:
        light_update(light)
        
        if rfid_reader is not None:
            if rfid_busy:
                rfid_busy = rfid_reader.is_present(100)
            else:
                spool = rfid_reader.poll()
                if spool is not None:
                    global_state.record_rfid_read(spool)
                    rfid_busy = True 

        global_state.mqtt_poll()
        await asyncio.sleep(0.10)

if not wifi_connect(wifi["ssid"], wifi["password"]):
    wifi_create_ap("rfid-spool-handler")

global_state = GlobalState()
asyncio.run(main())
