{% args filament, mqtt_error, wifi_error %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'filament', mqtt_error, wifi_error %}
    <h1>Filaments</h1>
    <div class="row">
        <div class="col col-1">ID</div>
        <div class="col col-1">type</div>
        <div class="col col-1">Brand</div>
        <div class="col col-2">Sub-type</div>
<!--
        <div class="col col-1">Color</div>
        <div class="col col-1">TD</div>
        <div class="col col-1">Temp</div>
        <div class="col col-1">Bed Temp</div>
-->
    </div>
{% for id, f in filament.items() %}
    <div class="row">
        <div class="col col-1">{[f['filament_id'] if 'filament_id' in f else '?']}</div>
        <div class="col col-1">{[f['type'] if 'type' in f else '']}</div>
        <div class="col col-1">{[f['brand'] if 'brand' in f else '']}</div>
        <div class="col col-2">{[f['subtype'] if 'subtype' in f else '']}</div>
<!--
        <div class="col col-1"><input type="color" readonly value="{[f.get('color_hex')]}" style="pointer-events: none" tabindex="-1"/></div>
        <div class="col col-1">{[f['td'] if 'td' in f else '']}</div>
        <div class="col col-1">{[f['min_temp'] if 'min_temp' in f else '0']}..{[f['max_temp'] if 'max_temp' in f else '0']}</div>
        <div class="col col-1">{[f['bed_min_temp'] if 'bed_min_temp' in f else '0']}..{[f['bed_max_temp'] if 'bed_max_temp' in f else '0']}</div>
        <div class="col col-1"><a href="/filament/edit?id={[id]}">edit</a>&nbsp;&nbsp;&nbsp;<a href="/filament/delete?id={[id]}">delete</a></div>
-->
    </div>
{% endfor %}
    <div class="row">
        <form action="/filament/add"><button type="submit">Add Filament</button></form>
    </div>
{% include "body-end.tpl" %}
</body>
</html>
