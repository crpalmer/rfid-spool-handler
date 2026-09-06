{% args model %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'printer', model %}
    <h1>Add Printer</h1>
    {% include "printer-form.tpl" '/printer/add', model %}
{% include "body-end.tpl" %}
</body>
</html>
