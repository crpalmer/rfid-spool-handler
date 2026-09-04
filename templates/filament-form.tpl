{% args action, id = None, f = {} %}
    <div class="form-container">
        <form action="{[action]}" method="post">
{% if id is not None %}
            <input type="hidden" name="id" value="{[id]}"/>
{% endif %}
            <label for="filament_id">filament_id (to match with OrcaSlicer)</label>
            <input id="filament_id" name="filament_id" type="text" placeholder="id (max 8)" pattern=".{1,8}" value="{[f.get('filament_id', '')]}" required />
            <label for="brand">Brand</label>
            <input id="brand" name="brand" type="text" placeholder="manufacturer" value="{[f.get('brand', '')]}" required />
            <label for="type">Type</label>
            <input id="type" name="type" type="text" placeholder="material type, e.g. PLA, PETG, PLA-S..." value="{[f.get('type', '')]}"  required />
            <label for="subtype">Sub-type</label>
            <input id="subtype" name="subtype" type="text" placeholder="subtype" value="{[f.get('subtype', '')]}" />
            <label for="color">Color</label>
            <input id="color" class="chota-color-picker" style="display: block" name="color_hex" type="color" value="{f.get('color_hex', '')]}"/>
            <label for="td">Transmission Distance (TD)</label>
            <input id="td" name="td" type="number" step="any" value="{[f.get('td', '')]}"/>
            <label for="min_temp">Nozzle Minimum Temperature</label>
            <input id="min_temp" name="min_temp" type="number" min="0" max="500" value="{[f.get('min_temp', '')]}"/>
            <label for="max_temp">Nozzle Maximum Temperature</label>
            <input id="max_temp" name="max_temp" type="number" min="0" max="500" value="{[f.get('max_temp', '')]}"/>
            <label for="bed_min_temp">Bed Minimum Temperature</label>
            <input id="bed_min_temp" name="bed_min_temp" type="number" min="0" max="200" value="{[f.get('bed_min_temp', '')]}"/>
            <label for="bed_max_temp">Bed Maximum Temperature</label>
            <input id="bed_max_temp" name="bed_max_temp" type="number" min="0" max="200" value="{[f.get('bed_max_temp', '')]}"/>
            <button type="submit">Save Filament</button>
        </form>
        <form action="/filament"><button type="submit">Cancel</button></form>
    </div>
