import json
import sys
import time
from umqtt.simple import MQTTClient

import ssl

class AMSTray:
    def __init__(self, tray_json):
        self._json = tray_json

    def is_empty(self):
        return self.get_type() == None

    def _get(self, key, default = None):
        return self._json[key] if key in self._json else default
    
    def get_id(self):
        return int(self._get("id", -1))
    
    def get_type(self):
        return self._get("tray_type")
    
    def get_color(self):
        return self._get("tray_color")
    
    def get_info_idx(self):
        return self._get("tray_info_idx")
    
    def get_nozzle_temps(self):
        return [ int(self._get("nozzle_temp_min", 0)), int(self._get("nozzle_temp_max", 0))]
    
    def __eq__(self, other):
        return self.get_id() == other.get_id() and self.get_type() == other.get_type() and self.get_color() == other.get_color() and self.get_info_idx() == other.get_info_idx() and self.get_nozzle_temps() == other.get_nozzle_temps()
                
    def __str__(self):
        return "<empty>" if self.is_empty() else f"({self.get_id()}, {self.get_type()}, {self.get_color()}, {self.get_info_idx()}, {self.get_nozzle_temps()})"

class BambuMQTT:
    def __init__(self):
        self._client = None
        
    def connect(self, ip, serial, access_code):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations(cafile="bbl.pem")

        self._channel = ("device/" + serial + "/request").encode()
        self._response_channel = ("device/" + serial + "/report").encode()

        self._client = MQTTClient("client", ip, port=8883, user="bblp", password=access_code, ssl=ssl_context)
        self._client.connect()
        self._client.set_callback(lambda topic, msg: self._on_message_callback(topic, msg))
        self._client.subscribe(self._response_channel)
        self._sequence = 0
        self.ams = {}
        self._response_handlers = {}

    def disconnect(self):
        if self._client is not None:
            self._client.disconnect()
        self._client = None
        
    def run(self):
        while True:
            self._client.wait_msg()

    def poll(self):
        self._client.check_msg()

    # Todo map sequence number to a callback function
    def make_request(self, type, command, extra = {}, handle_response = None):
        payload = { "sequence_id": str(self._sequence), "command": command } | extra
        request = { type: payload }
        if handle_response is not None:
            self._response_handlers[self._sequence] = handle_response
        self._sequence = self._sequence + 1
        print("publish " + str(self._channel) + " --> " + str(request))
        self._client.publish(self._channel, json.dumps(request).encode())

    def _spool_to_ams(self, extra, spool, key1, key2, transform = lambda x: x):
        if key1 in spool:
            extra[key2] = transform(spool[key1])

    def send_ams_filament_information(self, ams_id, tray_id, spool):
        extra = { "ams_id": ams_id, "tray_id": tray_id }
        self._spool_to_ams(extra, spool, "filament_id", "tray_info_idx")
        self._spool_to_ams(extra, spool, "color_hex", "tray_color", lambda color: color[:6] + "FF")
        self._spool_to_ams(extra, spool, "min_temp", "nozzle_temp_min", lambda s: int(s))
        self._spool_to_ams(extra, spool, "max_temp", "nozzle_temp_max", lambda s: int(s))
        self._spool_to_ams(extra, spool, "type", "tray_type")
        self.make_request("print", "ams_filament_setting", extra, lambda data: print(data))

    def _handle_info(self, info):
        if "command" in info and info["command"] == "get_version":
            for module in info["module"]:
                if module["visible"]:
                    print(module["product_name"] + ": " + module["sw_ver"])

    def _handle_status(self, prt):
        if "ams" not in prt or "ams" not in prt["ams"]:
            return
        for ams in prt["ams"]["ams"]:
            ams_id = int(ams["id"])
            
            initializing = False
            if ams_id not in self.ams:
                self.ams[ams_id] = {}
                initializing = True
                
            trays = self.ams[ams_id]
            for tray_json in ams["tray"]:
                tray = AMSTray(tray_json)
                tray_id = tray.get_id()
                if initializing:
                    trays[tray_id] = tray
                    print("initial tray " + str(tray))
                elif tray_id not in trays:
                    self.on_tray_change(ams_id, None, tray)
                    trays[tray_id] = tray
                elif trays[tray_id] != tray:
                    self.on_tray_change(ams_id, trays[tray_id], tray)
                    trays[tray_id] = tray

    def on_tray_change(self, ams_id, old_tray, new_tray):
        print(f"WRONG METHOD: ams {ams_id} changed {old_tray} -> {new_tray}")
        pass

    def _dispatch_handler(self, data):
        if "sequence_id" in data and data["sequence_id"] in self._response_handlers:
            handler = self._response_handlers.pop(data["sequence_id"])
            handler(data)
            return True
        return False
    
    def _on_message_callback(self, topic, msg_bytes):
#         try:
        msg = msg_bytes.decode()
        data = json.loads(msg)

        if self._dispatch_handler(data):
            return

        if "info" in data:
            if not self._dispatch_handler(data["info"]):
                self._handle_info(data["info"])
        elif "print" in data and "command" in data["print"]:
            if not self._dispatch_handler(data["print"]):
                if data["print"]["command"] == "push_status":
                    self._handle_status(data["print"])
                else:
                    print(f"unhandled data: {data}")
#         except Exception as e:
#             print("failed to parse json: " + str(e))