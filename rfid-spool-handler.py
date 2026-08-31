from microdot import Microdot
from microdot import Response

import json
import machine

from wifi import wifi_connect

wifi_connect()

Response.default_content_type = 'text/html'
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

