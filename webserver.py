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

def escape_html(text):
    if not isinstance(text, str):
        return text
    # Replace dangerous HTML characters with safe character entities
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#039;"))

@app.route('/')
async def index(request):
    return Template('index.tpl').render(mqtt_error=notifier.mqtt_error, wifi_error=notifier.wifi_error)

@app.route('/printer', methods=['GET', 'POST'])
async def printer_config(request):
    if request.form is not None:
        changed = False
        for key in [ "ip", "serial", "ac" ]:
            value = request.form.get(key)
            if value is not None:
                printer[key] = value
                changed = True
        if changed:
            with open("printer.json", "w") as f:
                json.dump(printer, f)
            notifier.on_printer_config_changed(printer)
    print(notifier.mqtt_error)
    return Template('printer.tpl').render(
                ip=escape_html(printer["ip"]), serial=escape_html(printer["serial"]),
                ac=escape_html(printer["ac"]),
                mqtt_error=notifier.mqtt_error, wifi_error=notifier.wifi_error
    )

def web_server_start(user_notifier):
    global notifier
    notifier = user_notifier
    notifier.on_printer_config_changed(printer)
    asyncio.create_task(app.start_server(port=80, debug=True))