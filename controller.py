import asyncio
import machine
import time

from bambu import BambuMQTT
from model import Model
from wifi import wifi_connect

class Controller:
    def __init__(self):
        self._model = Model()
        self.mqtt = BambuMQTT(self)
        self.mqtt_is_connected = False

    def set_filament(self, filament):
        self._model.set_filament(filament)

    def schedule_send_spool(self, ams_id, tray_id):
        self._model.schedule_send_spool(ams_id, tray_id)

    def get_spool_to_send(self):
        return self._model.get_spool_to_send()
    
    def send_spool_if_ready(self):
        (ams_id, tray_id, spool) = self._model.get_scheduled_send_spool_data()
        if ams_id >= 0 and spool is not None:
            print(f"Loading new spool information: {spool}")
            if "filament_id" not in spool:
                best_filament_id = self._model.find_filament_id_for_spool(spool)
                temp_spool = {}
                temp_spool.update(spool)
                temp_spool["filament_id"] = best_filament_id
                spool = temp_spool
            self.mqtt.send_ams_filament_information(ams_id, tray_id, spool)
            self._model.clear_spool_to_send()
        
    def record_rfid_read(self, spool):
        self._model.record_rfid_read(spool)

    def on_filament_config_changed(self, filament):
        model.set_filament(filament)

    def on_printer_config_changed(self, printer):
        model.set_printer_config(printer)
        self.connect(printer)

    def set_ams_tray(self, ams_id, tray):
        old_tray = self._model.set_ams_tray(ams_id, tray)
        if old_tray is not None and old_tray.is_empty() and not tray.is_empty():
            self.schedule_send_spool(ams_id, tray.get_id())

    def get_model(self):
        return self._model

    def add_filament(self, new_filament):
        self._model.add_filament(new_filament)

    def update_filament(self, id, new_filament):
        self._model.update_filament(id, new_filament)

    def delete_filament(self, id):
        self._model.delete_filament(id)

    def set_printer_config(self, printer):
        self._model.set_printer_config(printer)
        self._connect(printer)
    
    def _connect(self, printer):
#         try:
            print(f"Connecting to MQTT server: {printer["ip"]}")
            self.mqtt.disconnect()
            self.mqtt.connect(ip=printer["ip"], serial=printer["serial"], access_code=printer["ac"])
            self._model.set_mqtt_error(None)
            self.mqtt_is_connected = True
#         except Exception as e:
#             self._model.set_mqtt_error(str(e))
#             self.mqtt_is_connected = False
#             print(f"failed to connect to {printer["ip"]}: {e}")

    def set_wifi_config(self, wifi):
        self._model.set_wifi_config(wifi)
        asyncio.create_task(self._restart_task())
        
    async def _restart_task(self):
        await asyncio.sleep(2)
        machine.reset()
    
    async def run(self):
        wifi_connect(self._model.wifi)
        self._connect(self._model.get_printer_config())
        while True:
            if self.mqtt_is_connected:
                self.mqtt.poll()
                self.send_spool_if_ready()
            await asyncio.sleep_ms(100)

controller = Controller()