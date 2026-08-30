from microdot import Microdot
from microdot import Response

import network
import time

Response.default_content_type = 'text/html'

import json
import machine

def wifi_setup():
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
            machine.reset()
            return "<h1>Wifi Config Saved</h1>"
        return '<html><head><title>RFID Spool Handler (SETUP)</title></head><body><h1>RFID Spool Handler: Setup WiFi</h1><form><div>SSID: <input name="ssid" type="text" size="40"/></div><div>Password: <input name="password" type="password"/></div><input type="submit"/></form></body></html>'
    portal.run(port=80)

try:
    with open("wifi.json", "r") as f:
        config = json.load(f)
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        print("Trying to connect to SSID: " + config["ssid"])
        wlan.connect(config["ssid"], config["password"])
        timeout = 30
        while not wlan.isconnected():
            time.sleep(1)
            timeout -= 1
            if timeout <= 0:
                print("Couldn't connect to wifi, entering setup")
                wifi_setup()
except ValueError:
    print("Malformed JSON in wifi.json, entering setup")
    wifi_setup()
except OSError:
    print("No wifi.json, entering setup")
    wifi_setup()

print('Connected on IP:', wlan.ifconfig()[0])

app = Microdot()

@app.route('/')
async def index(request):
    return "<html>" + head_html + "<body>" + header_html + index_html.format() + "</body></html>"

@app.route('/settings/printer')
async def printer(request):
    return "<html>" + head_html + "<body>" + header_html + printer_settings_html.format() + "</body></html>"

head_html = """
<head>
  <title>RFID Spool Handler</title>
  <style>
.nav-link {
    padding: 10px;
}
</style>
</head>
"""

header_html = """
<h1>RFID Spool Handler</h1>
<div style="nav"><span class="nav-link"><a href="/">Home<a></span><span class="nav-link"><a href="/settings/printer">Setup Printer</a></span></div>
"""

index_html = """
<div>Front Page</div>
"""

printer_settings_html = """
<div>Printer settings</div>
"""

app.run(port=80)

