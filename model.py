import json
import time
import os

class SpoolToSend:
    def __init__(self):
        self.printer_id = None
        self.ams_id = -1
        self.tray_id = -1
        self.spool = None
        self.timeout = -1

    def ready(self, spool):
        self.spool = spool
        self.timeout = time.ticks_ms() + 5*60*1000

    def scheduled(self, printer_id, ams_id, tray_id):
        self.printer_id = str(printer_id) # this is a str in the json, just go with it
        self.ams_id = int(ams_id)
        self.tray_id = int(tray_id)
        
    def is_ready(self):
        return self.spool != None and self.timeout > time.ticks_ms()
    
    def is_scheduled(self):
        return self.is_ready() and self.printer_id is not None

    def __str__(self):
        return f"({self.printer_id}, {self.ams_id}, {self.tray_id}, {self.spool}, {self.timeout})"

class Model:
    def __init__(self):
        self.printer_ams = {}
        self.spool = SpoolToSend()
        self.new_spool_active_ms = 5*60*1000
        self.last_filament_id = None
        self.mqtt_error = {}
        self.transient_error = None
        self.rfid_error = None

        try:
            os.mkdir("data")
        except OSError as e:
                # Error number 17 represents 'File Exists' (EEXIST)
                if e.errno != 17:
                    raise # Re-raise if it's a different error

        self.filament = self._load_data("data/filament.json", {})
        self.printers = self._load_data("data/printers.json", {})
        self.wifi = self._load_data("data/wifi.json", { "ssid": "", "password": "" })

    def _load_data(self, filename, default):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except:
            data = default
        return data

    def set_filament(self, filament):
        self.filament = filament
        with open("data/filament.json", "w") as f:
            json.dump(filament, f)

    def set_printer_config(self, printer):
        self.printer = printer
        with open("data/printer.json", "w") as f:
            json.dump(printer, f)

    def schedule_send_spool(self, printer_id, ams_id, tray_id):
        if self.spool.is_ready():
            self.spool.scheduled(printer_id, ams_id, tray_id)
            print(f"scheduled send: {self.spool}")

    def record_rfid_read(self, spool):
        self.spool.ready(spool)
        print(f"queued new spool: {self.spool}")

    def get_ams(self, printer_id):
        return self.printer_ams.get(printer_id, {})
    
    def get_filament(self):
        return self.filament
    
    def get_wifi(self):
        return self.wifi
    
    def get_printers(self):
        return self.printers
    
    def get_last_filament_id(self):
        return self.last_filament_id
    
    def clear_spool_to_send(self):
        self.spool = SpoolToSend()

    def get_spool_to_send(self):
        return self.spool

    def set_ams_tray(self, printer_id, ams_id, tray):
        if printer_id not in self.printer_ams:
            self.printer_ams[printer_id] = {}
        printer_ams = self.get_ams(printer_id)
        if ams_id not in printer_ams:
            printer_ams[ams_id] = {}
        ams = printer_ams[ams_id]
        tray_id = tray.get_id()
        if tray_id not in ams:
            ams[tray_id] = tray
        elif tray != ams[tray_id]:
            old_tray = ams[tray_id]
            ams[tray_id] = tray
            self.last_filament_id = tray.get_info_idx()
            return old_tray
        return None
    
    def add_filament(self, new_filament):
        id = len(self.filament)
        while str(id) in self.filament:
            id += 1
        self.filament[str(id)] = new_filament
        self._save_filament()
        return id

    def update_filament(self, id, filament):
        self.filament[id] = filament
        self._save_filament()

    def delete_filament(self, id):
        self.filament.pop(id, None)
        self._save_filament()

    def _save_filament(self):
        with open("data/filament.json", "w") as f:
            json.dump(self.filament, f)

    def add_printer(self, printer):
        id = len(self.printers)
        while str(id) in self.printers:
            id += 1
        self.printers[str(id)] = printer
        self._save_printers()
        return id

    def update_printer(self, id, printer):
        self.printers[id] = printer
        self._save_printers()

    def delete_printer(self, id):
        self.printers.pop(id, None)
        self._save_printers()
    def _save_printers(self):
        with open("data/printers.json", "w") as f:
            json.dump(self.printers, f)

    def set_wifi_config(self, wifi):
        self.wifi = wifi
        with open("data/wifi.json", "w") as f:
            json.dump(wifi, f)

    def set_mqtt_error(self, printer_id, error):
        self.mqtt_error[printer_id] = error
    
    def clear_mqtt_error(self, printer_id):
        self.mqtt_error.pop(printer_id, None)
        
    def get_mqtt_error(self):
        return self.mqtt_error

    def add_transient_error(self, error):
        if self.transient_error is None:
            self.transient_error = error
        else:
            self.transient_error += f" | {error}"

    def get_transient_error(self):
        error = self.transient_error
        self.transient_error = None
        return error
    
    def set_rfid_error(self, error):
        self.rfid_error = error

    def get_rfid_error(self):
        return self.rfid_error
