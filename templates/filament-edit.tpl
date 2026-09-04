{% args id, filament, mqtt_error, wifi_error %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'filament', mqtt_error, wifi_error %}
    <h1>Edit Filament</h1>
    {% include "filament-form.tpl" '/filament/edit', id, filament %}
{% include "body-end.tpl" %}
</body>
</html>
