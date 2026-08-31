from microdot import Microdot
from microdot import Response

import asyncio
import json
import network
import time

def wifi_setup_via_portal():
    wlan = network.WLAN(network.WLAN.IF_AP)
    wlan.config(ssid="rfid-spool-handler", password="password")
    wlan.active(True)
    portal = Microdot()
    @portal.route('/')
    async def index(request):
        if "ssid" in request.args and "password" in request.args:
            config = { "ssid": request.args["ssid"], "password": request.args["password"] }
            with open("wifi.json", "w") as f:
                json.dump(config, f)
            request.app.shutdown()
            return "<h1>Wifi Config Saved</h1>", { "content-type": "text/html" }
        return '<html><head><title>RFID Spool Handler (SETUP)</title></head><body><h1>RFID Spool Handler: Setup WiFi</h1><form><div>SSID: <input name="ssid" type="text" size="40"/></div><div>Password: <input name="password" type="password"/></div><input type="submit"/></form></body></html>', { "content-type": "text/html" }
    portal.run(port=80, debug=True)
    print("Captive portal shut down")

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
            
    while not wlan.isconnected():
        try:
            with open("wifi.json", "r") as f:
                config = json.load(f)
                print("Trying to connect to SSID: " + config["ssid"])
                wlan.connect(config["ssid"], config["password"])
                timeout = 30
                while not wlan.isconnected():
                    time.sleep(1)
                    timeout -= 1
                    if timeout <= 0:
                        print("Couldn't connect to wifi, entering setup")
                        wifi_setup_via_portal()
        except ValueError:
            print("Malformed JSON in wifi.json, entering setup")
            wifi_setup_via_portal()
        except OSError:
            print("No wifi.json, entering setup")
            wifi_setup_via_portal()

    print('Connected on IP:', wlan.ifconfig()[0])
