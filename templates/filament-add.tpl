{% args model %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'filament', model %}
{% if model.get_last_filament_id() is not None %}
    <div class="col col4 is-left">
        <div class="card">
            <header><h4>Last Seen Filament ID</h4></header>
            <p>{[model.get_last_filament_id()]}</p>
        </div>
    </div>
{% endif %}
    <h1>Add Filament</h1>
    {% include "filament-form.tpl" '/filament/add', model %}
{% include "body-end.tpl" %}
</body>
</html>
