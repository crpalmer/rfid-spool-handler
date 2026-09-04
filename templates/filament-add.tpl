{% args filament, mqtt_error, wifi_error %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'filament', mqtt_error, wifi_error %}
    <h1>Add Filament</h1>
    {% include "filament-form.tpl" '/filament/add' %}
{% include "body-end.tpl" %}
</body>
</html>
