import asyncio
import json
from mqtt import MQTTClient
import ssl
import sys

from amstray import AMSTray

class BambuMQTT:
    def __init__(self):
        self._client = None
        self._sequence = 0
        self._response_handlers = {}
        
    async def connect(self, ip, serial, access_code):
        if ip is None or ip == "":
            return
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations(cafile="bbl.pem")

        self._channel = ("device/" + serial + "/request").encode()
        self._response_channel = ("device/" + serial + "/report").encode()

        self._client = MQTTClient("client", ip, port=8883, user="bblp", password=access_code, ssl=ssl_context)
        await self._client.connect()
        self._client.set_callback(lambda topic, msg: self._on_message_callback(topic, msg))
        await self._client.subscribe(self._response_channel)
        await self.make_request("pushing", "pushall", { "version": 1, "push_target": 1 })
        await self.make_request("info", "get_version")

    async def disconnect(self):
        if self._client is not None:
            self._client.disconnect()
        self._client = None
        
    async def poll(self):
        await self._client.wait_msg()

    # Todo map sequence number to a callback function
    async def make_request(self, type, command, extra = {}, handle_response = None):
        payload = { "sequence_id": str(self._sequence), "command": command } | extra
        request = { type: payload }
        if handle_response is not None:
            self._response_handlers[self._sequence] = handle_response
        self._sequence = self._sequence + 1
        print("publish " + str(self._channel) + " --> " + str(request))
        await self._client.publish(self._channel, json.dumps(request).encode())

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
            for tray in ams["tray"]:
                self.set_ams_tray(ams_id, AMSTray(tray))

    def set_ams_tray(self, ams_id, tray):
        pass

    def _dispatch_handler(self, data):
        if "sequence_id" in data and data["sequence_id"] in self._response_handlers:
            handler = self._response_handlers.pop(data["sequence_id"])
            handler(data)
            return True
        return False
    
    def _on_message_callback(self, topic, msg_bytes):
        msg = msg_bytes.decode()
        try:
            data = json.loads(msg)
        except Exception as e:
            print("failed to parse json: " + str(e))
            print(msg)
            sys.print_exception(e)
            return
 
        if self._dispatch_handler(data):
            return
        if "info" in data:
            if not self._dispatch_handler(data["info"]):
                self._handle_info(data["info"])
        elif "print" in data and "command" in data["print"]:
            if not self._dispatch_handler(data["print"]):
                if data["print"]["command"] == "push_status":
                    self._handle_status(data["print"])
