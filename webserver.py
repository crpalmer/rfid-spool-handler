from microdot.microdot import Microdot, Response
from microdot.utemplate import Template

import asyncio
import json
import machine

class WebServerNotifier:
    def __init__(self):
        self.mqtt_error = None
        self.wifi_error = None
        
    def on_printer_config_changed(self, printer):
        pass
    def on_filament_changed(self, filament):
        pass

Response.default_content_type = 'text/html'
app = Microdot()
notifier = None

try:
    with open("printer.json", "r") as f:
        printer = json.load(f)
except:
    printer = { "ip": "", "serial": "", "ac": "" }

try:
    with open("wifi.json", "r") as f:
        wifi = json.load(f)
except:
    wifi = { "ssid": "", "password": "" }

def form_to_json(request, keys, data, filename):
    if request.form is None:
        return False
    changed = False
    for key in keys:
        value = request.form.get(key)
        if value is not None:
            if key not in data or data[key] != value:
                changed = True
            data[key] = value
    if changed:
        with open(filename, "w") as f:
            json.dump(data, f)
    return changed

@app.route('/')
async def index(request):
    return Template('index.tpl').render(mqtt_error=notifier.mqtt_error, wifi_error=notifier.wifi_error)

@app.route('/printer', methods=['GET', 'POST'])
async def printer_config(request):
    if form_to_json(request, [ "ip", "serial", "ac" ], printer, "printer.json"):
        notifier.on_printer_config_changed(printer)
    return Template('printer.tpl').render(
                ip=printer["ip"], serial=printer["serial"], ac=printer["ac"],
                mqtt_error=notifier.mqtt_error, wifi_error=notifier.wifi_error
    )

async def restart():
    await asyncio.sleep(5)
    machine.reset()
    
@app.route('/wifi', methods=['GET', 'POST'])
async def wifi_config(request):
    if request.form is not None:
        if form_to_json(request, [ "ssid", "password" ], wifi, "wifi.json"):
            asyncio.create_task(restart())
    return Template('wifi.tpl').render(
                ssid=wifi["ssid"], password=wifi["password"],
                mqtt_error=notifier.mqtt_error, wifi_error=notifier.wifi_error
    )

def web_server_start(user_notifier):
    global notifier
    notifier = user_notifier
    notifier.on_printer_config_changed(printer)
    asyncio.create_task(app.start_server(port=80, debug=True))