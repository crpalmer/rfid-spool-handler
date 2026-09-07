{% args model %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'wifi', model %}
{% set wifi = model.get_wifi() %}
    <h1>WiFi Setup</h1>
    <div class="form-container">
        <form action="#" method="post">
            <label for="ssid">SSID (required)</label>
            <input id="ssid" name="ssid" type="text" size="20" placeholder="your-ssid" required value="{[wifi["ssid"]]}" />
            <label for="password">Password</label>
            <input id="password" name="password" type="password" size="20" placeholder="xxxxxxxxxxxxxxx" value="{[wifi["password"]]}" />
            <label for="hostname">Hostname</label>
            <input id="hostname" name="hostname" value="{[wifi.get("hostname", "")]}"/>
            <p>&nbsp;</p>
            <button type="submit">Save</button>
        </form>
    </div>
{% include "body-end.tpl" %}
</body>
</html>
