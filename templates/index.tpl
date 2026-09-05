{% args model %}
<html>
{% include "head.partial" %}
    <body>
{% include "body-start.tpl" '/', model %}
        <h1>Status</h1>
{% set pending_spool = model.get_spool_to_send() %}
{% if pending_spool is not None %}
        <h3>Pending Spool Load</h3>
        <div class="row">
          <div class="col col-1">&nbsp;</div>
          <div class="col">
              <input type="color" readonly value="#{[pending_spool.get('color_hex')]}" style="pointer-events: none" tabindex="-1"/>
              {[pending_spool.get('type')]}: {[pending_spool.get('brand')]} {[pending_spool.get('subtype', '')]}
          </div>
        </div>
        <h3>AMS State</h4>
{% endif %}
{% set filament = model.get_filament() %}
{% set ams = model.get_ams() %}
{% for ams_id in sorted(ams.keys()) %}
        <h4>AMS #{[ams_id+1]}</h4>
  {% for id in sorted(ams[ams_id].keys()) %}
    {% set tray = ams[ams_id][id] %}
        <div class="row">
            <div class="col col-1 text-right">{[id+1]}</div>
       {% if tray.is_empty() %}
            <div class="col">**empty**</div>
       {% else %}
            <div class="col">
                <input type="color" readonly value="#{[tray.get_color()[0:6]]}" style="pointer-events: none" tabindex="-1"/>
                {[tray.get_type()]}:
          {% set matching = {k: v for k, v in filament.items() if v.get('filament_id') == tray.get_info_idx()} %}
          {% if len(matching) >= 1 %}
             {% set f = next(iter(matching.values())) %}
                {[f.get('brand', "(unknown)")]} {[f.get('subtype', '')]}
          {% endif %}
            </div>
       {% endif %}
        </div>
  {% endfor %}
{% endfor %}
{% include "body-end.tpl" %}
    </body>
</html>
