{% args mqtt_error, wifi_error %}
<html>
{% include "head.partial" %}
    <body>
{% include "body-start.tpl" '/', mqtt_error, wifi_error %}
        <h1>Test</h1>
{% include "body-end.tpl" %}
    </body>
</html>