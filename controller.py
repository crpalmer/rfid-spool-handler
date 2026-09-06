import asyncio
import machine
import time

from bambu import BambuMQTT
from model import Model
from wifi import wifi_connect

class Controller:
    class Printer(BambuMQTT):
        def __init__(self, model, controller, printer_id):
            super().__init__()
            self.INIT = 0
            self.CONFIGURED = 1
            self.ACTIVE = 2
            self.ERROR = 3
            self._model = model
            self._state = self.INIT
            self._id = printer_id
            self._config = None
            self._has_error = False

        def set_config(self, config):
            self._config = config
            self._state = self.CONFIGURED
            
        def disconnect(self):
            if self._state == self.ACTIVE:
                super().disconnect()
            self._state = self.INIT
            
        def connect(self):
            try:
                print(f"Connecting to MQTT server: {self._config["name"]} @ {self._config["ip"]}")
                self.disconnect()
                super().connect(ip=self._config["ip"], serial=self._config["serial"], access_code=self._config["ac"])
                self._model.clear_mqtt_error(self._id)
                self._state = self.ACTIVE
            except Exception as e:
                self._model.set_mqtt_error(self._id, str(e))
                self.state = self.ERROR
                print(f"failed to connect to {self._config["ip"]}: {e}")

        def set_ams_tray(self, ams_id, tray):
            old_tray = self._model.set_ams_tray(self._id, ams_id, tray)
            if old_tray is not None and old_tray.is_empty():
                controller.schedule_send_spool(self._id, ams_id, tray.get_id())

        def poll(self):
            if self._state == self.CONFIGURED:
                self.connect()
            if self._state == self.ACTIVE:
                super().poll()

    def __init__(self):
        self._model = Model()
        self._printers = {}

    def set_filament(self, filament):
        self._model.set_filament(filament)

    def schedule_send_spool(self, printer_id, ams_id, tray_id):
        self._model.schedule_send_spool(printer_id, ams_id, tray_id)

    def find_filament_id_for_spool(self, spool):
        best = None
        best_quality = -1
        for f in self._model.get_filament().values():
            if 'filament_id' in f and f.get('brand') == spool.get('brand') and f.get('type') == spool.get('type'):
                quality = 0
                quality += 1 if f.get('subtype') == spool.get('subtype') else 0
                quality += 2 if f.get('color_hex') == spool.get('color_hex') else 0
                if quality > best_quality:
                    best = f
                    best_quality = quality

        return best['filament_id'] if best is not None else None

    def get_spool_to_send(self):
        return self._model.get_spool_to_send()

    def send_spool_if_ready(self):
        spool = self.get_spool_to_send()
        if spool.is_scheduled():
            print(f"Loading new spool information: {spool}")
            if "filament_id" not in spool.spool:
                best_filament_id = self.find_filament_id_for_spool(spool.spool)
                temp_spool = {}
                temp_spool.update(spool.spool)
                temp_spool["filament_id"] = best_filament_id
            self._printers[spool.printer_id].send_ams_filament_information(spool.ams_id, spool.tray_id, temp_spool)
            self._model.clear_spool_to_send()

    def record_rfid_read(self, spool):
        self._model.record_rfid_read(spool)

    def get_model(self):
        return self._model

    def add_filament(self, new_filament):
        self._model.add_filament(new_filament)

    def update_filament(self, id, new_filament):
        self._model.update_filament(id, new_filament)

    def delete_filament(self, id):
        self._model.delete_filament(id)

    def add_printer(self, printer):
        if len([p for p in self._model.get_printers().values() if p.get("ip") == printer.get("ip")]) > 0:
            self._model.add_transient_error(f"IP address {printer["ip"]} already exists")
        else:
            id = self._model.add_printer(printer)
            self._printers[id] = self.Printer(self._model, self, id, printer)

    def update_printer(self, id, printer):
        self._model.update_printer(id, printer)
        self._printers[id].disconnect()
        self._printers[id].set_config(printer)

    def delete_printer(self, id):
        self._model.delete_printer(id)
        self._printers[id].disconnect()
        self._printers.pop(id, None)
        
    def set_wifi_config(self, wifi):
        self._model.set_wifi_config(wifi)
        asyncio.create_task(self._restart_task())
        
    async def _restart_task(self):
        await asyncio.sleep(2)
        machine.reset()
    
    async def run(self):
        wifi_connect(self._model.wifi)
        for (id, printer) in self._model.get_printers().items():
            self._printers[id] = self.Printer(self._model, self, id)
            self._printers[id].set_config(printer)
        while True:
            for printer in self._printers.values():
                printer.poll()
            self.send_spool_if_ready()
            await asyncio.sleep_ms(100)

controller = Controller()