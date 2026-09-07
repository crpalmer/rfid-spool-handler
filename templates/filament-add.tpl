{% args model %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'filament', model %}
    <h1>Add Filament</h1>
    {% include "filament-form.tpl" '/filament/add', model %}
{% include "body-end.tpl" %}
</body>
</html>
