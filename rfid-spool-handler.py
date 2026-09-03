from microdot.microdot import Microdot, Response
from microdot.utemplate import Template

import asyncio
import json
import machine

from wifi import wifi_connect

wifi_connect()

Response.default_content_type = 'text/html'
app = Microdot()

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
    return Template('index.html').render()

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
    return Template('printer.html').render(ip=escape_html(printer["ip"]), serial=escape_html(printer["serial"]), ac=escape_html(printer["ac"]))

async def main():
    asyncio.create_task(app.start_server(port=80))
    while True:
        print("still here")
        await asyncio.sleep(10)

asyncio.run(main())
