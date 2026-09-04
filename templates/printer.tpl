{% args ip, serial, ac, mqtt_error, wifi_error %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'printer', mqtt_error, wifi_error %}
    <h1>Printer Setup</h1>
    <div class="form-container">
        <form action="#" method="post">
            <label for="ip">IP Address</label>
            <input id="ip" name="ip" type="text" size="20" pattern="[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}" placeholder="xxx.xxx.xxx.xxx" required value="{{ip}}" />
            <label for="serial">Serial #</label>
            <input id="serial" name="serial" type="text" size="20" placeholder="xxxxxxxxxxxxxxx" value="{{serial}}" />
            <label for="ac">Access Code</label>
            <input id="ac" name="ac" type="text" size="20" pattern="[0-9a-fA-F]{8}" placeholder="xxxxxxxx" required value="{{ac}}" />
            <p>&nbsp;</p>
            <button type="submit">Save</button>
        </form>
    </div>
{% include "body-end.tpl" %}
</body>
</html>
