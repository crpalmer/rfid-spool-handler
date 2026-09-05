{% args id, model %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'filament', model %}
    <h1>Edit Filament</h1>
    {% include "filament-form.tpl" '/filament/edit', model, id %}
{% include "body-end.tpl" %}
</body>
</html>
