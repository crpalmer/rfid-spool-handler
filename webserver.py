from microdot.microdot import Microdot, Response
from microdot.utemplate import Template
from controller import controller

import asyncio
import json
import machine
import os

Response.default_content_type = 'text/html'
app = Microdot()

filament_args = [ "filament_id", "brand", "type", "subtype", "color_hex", "td", "min_temp", "max_temp", "bed_min_temp", "bed_max_temp" ]
printer_args = [ "name", "ip", "serial", "ac" ]

def form_to_json(request, keys, data):
    if request.form is None:
        return False
    changed = False
    for key in keys:
        value = request.form.get(key)
        if value is not None:
            if (key not in data and value != "") or (key in data and data[key] != value):
                changed = True
                data[key] = value
    return changed

@app.route('/')
async def index(request):
    return Template('index.tpl').render(controller.get_model())

@app.route('/filament')
async def filament_list(request):
    return Template('filament.tpl').render(controller.get_model())

@app.route('/filament/add', methods=['GET', 'POST'])
async def filament_add(request):
    new_filament = {}
    if form_to_json(request, filament_args, new_filament):
        controller.add_filament(new_filament)
        return Response.redirect('/filament')
    return Template('filament-add.tpl').render(controller.get_model())

@app.route('/filament/edit', methods=['GET', 'POST'])
async def filament_edit(request):
    id = request.form.get("id") if request.form is not None else None
    if id is not None:
        new_filament = {}
        if form_to_json(request, filament_args, new_filament):
            controller.update_filament(id, new_filament)
            return Response.redirect('/filament')

    id = request.args.get("id") if request.args is not None else None
    if id is not None:
        return Template('filament-edit.tpl').render(id, controller.get_model())
    return Response.redirect("/filament")

@app.route('/filament/delete')
async def filament_delete(request):
    if "id" in request.args:
        controller.delete_filament(request.args["id"])
    return Response.redirect("/filament")

@app.route('/printer/add', methods=['GET', 'POST'])
async def printer_add(request):
    printer = {}
    if form_to_json(request, printer_args, printer):
        controller.add_printer(printer)
        return Response.redirect('/printer')
    return Template('printer-add.tpl').render(controller.get_model())

@app.route('/printer/edit', methods=['GET', 'POST'])
async def printer_edit(request):
    id = request.form.get("id") if request.form is not None else None
    if id is not None:
        printer = {}
        if form_to_json(request, printer_args, printer):
            print(printer)
            controller.update_printer(id, printer)
            return Response.redirect('/printer')

    id = request.args.get("id") if request.args is not None else None
    if id is not None:
        return Template('printer-edit.tpl').render(id, controller.get_model())
    return Response.redirect("/printer")

@app.route('/printer/delete')
async def printer_delete(request):
    if "id" in request.args:
        controller.delete_printer(request.args["id"])
    return Response.redirect("/printer")

@app.route('/printer', methods=['GET', 'POST'])
async def printer_config(request):
    printer = {}
    if form_to_json(request, [ "ip", "serial", "ac" ], printer):
        controller.set_printer_config(printer)
    return Template('printer.tpl').render(controller.get_model())

@app.route('/wifi', methods=['GET', 'POST'])
async def wifi_config(request):
    wifi = {}
    if form_to_json(request, [ "ssid", "password" ], wifi):
        controller.set_wifi_config(wifi)
    return Template('wifi.tpl').render(controller.get_model())

def web_server_start():
    asyncio.create_task(app.start_server(port=80, debug=False))
