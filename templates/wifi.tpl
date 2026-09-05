{% args ssid, password, mqtt_error, wifi_error %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'wifi', mqtt_error, wifi_error %}
    <h1>WiFi Setup</h1>
    <div class="form-container">
        <form action="#" method="post">
            <label for="ssid">SSID</label>
            <input id="ssid" name="ssid" type="text" size="20" placeholder="your-ssid" required value="{[ssid]}" />
            <label for="password">Password</label>
            <input id="password" name="password" type="password" size="20" placeholder="xxxxxxxxxxxxxxx" value="{[password]}" />
            <p>&nbsp;</p>
            <button type="submit">Save</button>
        </form>
    </div>
{% include "body-end.tpl" %}
</body>
</html>
