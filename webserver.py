from microdot.microdot import Microdot, Response
from microdot.utemplate import Template

import asyncio
import json
import machine
import os

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
state = None

try:
    os.mkdir("data")
except OSError as e:
        # Error number 17 represents 'File Exists' (EEXIST)
        if e.errno != 17:
            raise # Re-raise if it's a different error
def load_data(filename, default):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except:
        data = default
    return data

filament = load_data("data/filament.json", {})
printer = load_data("data/printer.json", { "ip": "", "serial": "", "ac": "" })
wifi = load_data("data/wifi.json", { "ssid": "", "password": "" })

def form_to_json(request, keys, data, filename = None):
    if request.form is None:
        return False
    changed = False
    for key in keys:
        value = request.form.get(key)
        if value is not None:
            if (key not in data and value != "") or (key in data and data[key] != value):
                changed = True
                data[key] = value
    if changed and filename is not None:
        with open(filename, "w") as f:
            json.dump(data, f)
    return changed

@app.route('/')
async def index(request):
    return Template('index.tpl').render(ams=state.mqtt.ams, filament=filament, pending=state.spool, mqtt_error=notifier.mqtt_error, wifi_error=notifier.wifi_error)

@app.route('/filament')
async def filament_list(request):
    print(filament)
    return Template('filament.tpl').render(
                filament=filament, mqtt_error=notifier.mqtt_error, wifi_error=notifier.wifi_error
    )

@app.route('/filament/add', methods=['GET', 'POST'])
async def filament_add(request):
    new_filament = {}
    if form_to_json(request, [ "filament_id", "brand", "type", "subtype", "color_hex", "td", "min_temp", "max_temp", "bed_min_temp", "bed_max_temp" ], new_filament):
        print(new_filament)
        id = len(filament)
        while str(id) in filament:
            id += 1
        filament[str(id)] = new_filament
        with open("data/filament.json", "w") as f:
            json.dump(filament, f)
        notifier.on_filament_config_changed(filament)
        return Response.redirect("/filament")
    return Template('filament-add.tpl').render(
                filament=filament, mqtt_error=notifier.mqtt_error, wifi_error=notifier.wifi_error
    )

@app.route('/filament/edit', methods=['GET', 'POST'])
async def filament_edit(request):
    id = request.form.get("id") if request.form is not None else None
    print(f"form {id}")
    if id is not None and id in filament:
        if form_to_json(request, [ "filament_id", "brand", "type", "subtype", "color_hex", "td", "min_temp", "max_temp", "bed_min_temp", "bed_max_temp" ], filament[id]):
            with open("data/filament.json", "w") as f:
                json.dump(filament, f)
            notifier.on_filament_config_changed(filament)
    if request.args is not None and "id" in request.args:
        id = request.args["id"]
        print(f"request {id}")
        if id in filament:
            return Template('filament-edit.tpl').render(
                id=id, filament=filament[id], mqtt_error=notifier.mqtt_error, wifi_error=notifier.wifi_error
            )
    return Response.redirect("/filament")

@app.route('/filament/delete')
async def filament_delete(request):
    if "id" in request.args:
        filament.pop(request.args["id"], None)
        with open("data/filament.json", "w") as f:
            json.dump(filament, f)
        notifier.on_filament_config_changed(filament)
    return Response.redirect("/filament")

@app.route('/printer', methods=['GET', 'POST'])
async def printer_config(request):
    if form_to_json(request, [ "ip", "serial", "ac" ], printer, "data/printer.json"):
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
        if form_to_json(request, [ "ssid", "password" ], wifi, "data/wifi.json"):
            asyncio.create_task(restart())
    return Template('wifi.tpl').render(
                ssid=wifi["ssid"], password=wifi["password"],
                mqtt_error=notifier.mqtt_error, wifi_error=notifier.wifi_error
    )

def web_server_start(user_notifier, global_state):
    global notifier, state
    notifier = user_notifier
    state = global_state
    notifier.on_filament_config_changed(filament)
    notifier.on_printer_config_changed(printer)
    asyncio.create_task(app.start_server(port=80, debug=True))