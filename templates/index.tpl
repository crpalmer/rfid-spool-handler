{% args model %}
<html>
{% include "head.partial" %}
    <body>
{% include "body-start.tpl" '/', model %}
        <h1>Status</h1>
{% set spool = model.get_spool_to_send() %}
{% if spool.is_ready() %}
        <h2>Pending Spool Load</h2>
        <div class="row">
          <div class="col col-1">&nbsp;</div>
          <div class="col">
              <input type="color" readonly value="#{[spool.spool.get('color_hex')]}" style="pointer-events: none" tabindex="-1"/>
              {[spool.spool.get('type')]}: {[spool.spool.get('brand')]} {[spool.spool.get('subtype', '')]}
          </div>
        </div>
        <h2>AMS State</h2>
{% endif %}
{% set filament = model.get_filament() %}
{% for (id, printer) in model.get_printers().items() %}
  {% set ams = model.get_ams(id) %}
    <h3>{[printer.get("name")]}</h3>
  {% for ams_id in sorted(ams.keys()if ams is not None else {}) %}
        <div class="row">
            <div class="col col-1">
                <h4>AMS #{[ams_id+1]}</h4>
            </div>
            <div class="col col-9"><div class="row">
    {% for id in sorted(ams[ams_id].keys()) %}
      {% set tray = ams[ams_id][id] %}
                <div class="col col-3">
                    {[id+1]}&nbsp;
      {% if tray.is_empty() %}
                    **empty**
      {% else %}
                    <input type="color" readonly value="#{[tray.get_color()[0:6]]}" style="pointer-events: none" tabindex="-1"/>
                    {[tray.get_type()]}
        {% set matching = {k: v for k, v in filament.items() if v.get('filament_id') == tray.get_info_idx()} %}
        {% if len(matching) >= 1 %}
          {% set f = next(iter(matching.values())) %}
                    : {[f.get('brand', "(unknown)")]} {[f.get('subtype', '')]}
        {% endif %}
      {% endif %}
                </div>
    {% endfor %}
            </div></div>
        </div>
  {% endfor %}
{% endfor %}
{% include "body-end.tpl" %}
    </body>
</html>
