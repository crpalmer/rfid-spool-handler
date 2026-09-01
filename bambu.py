import asyncio
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
    def __init__(self, ip, serial, access_code):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations(cafile="bbl.pem")

        self._channel = ("device/" + serial + "/request").encode()
        self._response_channel = ("device/" + serial + "/report").encode()

        self._client = MQTTClient("client", "192.168.1.22", port=8883, user="bblp", password=access_code, ssl=ssl_context)
        self._client.connect()
        self._client.set_callback(lambda topic, msg: self._on_message_callback(topic, msg))
        self._client.subscribe(self._response_channel)
        self._sequence = 0
        self._ams = {}

    def run(self):
        while True:
            self._client.wait_msg()

    def poll(self):
        self._client.check_msg()

    # Todo map sequence number to a callback function
    def make_request(self, type, command, extra = {}):
        request = { type: { "sequence_id": str(self._sequence), "command": command } }
        self._sequence = self._sequence + 1
        print("publish " + str(self._channel) + " --> " + str(request))
        self._client.publish(self._channel, json.dumps(request).encode())

    def _handle_info(self, info):
        if "command" in info and info["command"] == "get_version":
            for module in info["module"]:
                if module["visible"]:
                    print(module["product_name"] + ": " + module["sw_ver"])

    def _handle_print(self, prt):
        if "ams" not in prt or "ams" not in prt["ams"]:
            return
        for ams in prt["ams"]["ams"]:
            ams_id = ams["id"]
            
            initializing = False
            if ams_id not in self._ams:
                self._ams[ams_id] = {}
                initializing = True
                
            trays = self._ams[ams_id]
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

    def _on_message_callback(self, topic, msg_bytes):
        try:
            msg = msg_bytes.decode()
            data = json.loads(msg)
            if "info" in data:
                self._handle_info(data["info"])
            elif "print" in data:
                self._handle_print(data["print"])
        except Exception as e:
            print("failed to parse json: " + str(e))
