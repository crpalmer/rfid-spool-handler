{% args id, model %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'printer', model %}
    <h1>Edit Printer</h1>
    {% include "printer-form.tpl" '/printer/edit', model, id %}
{% include "body-end.tpl" %}
</body>
</html>
