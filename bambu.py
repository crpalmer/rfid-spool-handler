import asyncio
import json
import sys
import time
from umqtt.simple import MQTTClient
from wifi import wifi_connect

import ssl

wifi_connect()

class AMSTray:
    def __init__(self, tray_id, filament_type=None, color=None, info_idx=None, nozzle_temp_max=0, nozzle_temp_min=0):
        self.tray_id = tray_id
        self.type = filament_type
        self.color = color
        self.info_idx = info_idx
        self.nozzle_temp_max = nozzle_temp_max
        self.nozzle_temp_min = nozzle_temp_min
    
    @classmethod
    def from_json(cls, tray):
#        print(tray)
        tray_id = tray["id"]
        tray_type = tray["tray_type"] if "tray_type" in tray else None
        color = tray["tray_color"] if "tray_color" in tray else None
        info_idx = tray["tray_info_idx"] if "tray_info_idx" in tray else None
        nozzle_temp_max = int(tray["nozzle_temp_max"]) if "nozzle_temp_max" in tray else 0
        nozzle_temp_min = int(tray["nozzle_temp_min"]) if "nozzle_temp_min" in tray else 0
        return cls(tray_id, tray_type, color, info_idx, nozzle_temp_max, nozzle_temp_min)
    
    def __eq__(self, other):
        return self.tray_id == other.tray_id and self.type == other.type and self.color == other.color and self.info_idx == other.info_idx and self.nozzle_temp_max == other.nozzle_temp_max and self.nozzle_temp_min == other.nozzle_temp_min
                
    def __str__(self):
        return f"({self.tray_id}, {self.type}, {self.color}, {self.info_idx}, {self.nozzle_temp_min}..{self.nozzle_temp_max})"

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
                tray = AMSTray.from_json(tray_json)
                if initializing:
                    trays[tray.tray_id] = tray
                    print("initial tray " + str(tray))
                elif tray.tray_id not in trays:
                    trays[tray.tray_id] = tray
                    print("new tray " + str(tray))
                elif trays[tray.tray_id] != tray:
                    print("changed tray " + str(tray))
                    trays[tray.tray_id] = tray

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


mqtt = BambuMQTT("192.168.1.22", serial="0948AD561200005", access_code="75875fca")
mqtt.make_request("info", "get_version")
mqtt.run()