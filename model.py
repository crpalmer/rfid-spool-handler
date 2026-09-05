import json
import time
import os

class Model:
    def __init__(self):
        self.ams = {}
        self.spool = None
        self.spool_timeout = -1
        self.new_spool_active_ms = 5*60*1000
        self.send_to_ams_id = -1
        self.send_to_tray_id = -1
        self.filament = {}
        self.last_filament_id = None
        self.mqtt_error = None

        try:
            os.mkdir("data")
        except OSError as e:
                # Error number 17 represents 'File Exists' (EEXIST)
                if e.errno != 17:
                    raise # Re-raise if it's a different error

        self.filament = self._load_data("data/filament.json", {})
        self.printer = self._load_data("data/printer.json", { "ip": "", "serial": "", "ac": "" })
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

    def spool_is_sendable(self):
        return self.spool != None and time.ticks_ms() <= self.spool_timeout and self.send_to_ams_id < 0

    def schedule_send_spool(self, ams_id, tray_id):
        self.send_to_ams_id = ams_id
        self.send_to_tray_id = tray_id
        print(f"scheduled send to ({self.send_to_ams_id}, {self.send_to_tray_id}) for {self.spool}")

    def record_rfid_read(self, spool):
        self.spool = spool
        self.spool_timeout = time.ticks_ms() + new_spool_active_ms
        print(f"queued new spool until {self.spool_timeout}ms: {self.spool}")

    def get_ams(self):
        return self.ams
    
    def get_filament(self):
        return self.filament
    
    def get_wifi(self):
        return self.wifi
    
    def get_printer_config(self):
        return self.printer
    
    def get_last_filament_id(self):
        return self.last_filament_id
    
    def get_spool_to_send(self):
        if self.get_spool_ready_ms() >= time.ticks_ms():
            return self.spool
        return None

    def get_spool_ready_ms(self):
        return self.spool_timeout - time.ticks_ms() if self.spool is not None else 0

    def clear_spool_to_send(self):
        self.send_to_ams_id = -1
        self.spool = None

    def set_ams_tray(self, ams_id, tray):
        if ams_id not in self.ams:
            self.ams[ams_id] = {}
        ams = self.ams[ams_id]
        tray_id = tray.get_id()
        if tray_id not in ams:
            ams[tray_id] = tray
            return None
        else:
            old_tray = ams[tray_id]
            ams[tray_id] = tray
            self.last_filament_id = tray.get_info_idx()
            return old_tray

    def add_filament(self, new_filament):
        id = len(self.filament)
        while str(id) in self.filament:
            id += 1
        self.filament[str(id)] = new_filament
        self._save_filament()

    def update_filament(self, id, filament):
        self.filament[id] = filament
        self._save_filament()

    def delete_filament(self, id):
        self.filament.pop(id, None)
        self._save_filament()

    def _save_filament(self):
        with open("data/filament.json", "w") as f:
            json.dump(self.filament, f)

    def set_wifi_config(self, wifi):
        self.wifi = wifi
        with open("data/wifi.json", "w") as f:
            json.dump(wifi, f)

    def set_mqtt_error(self, error):
        self.mqtt_error = error