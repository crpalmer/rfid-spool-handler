{% args url, mqtt_error, wifi_error %}
<div class="row">
    <div class="col col-1">&nbsp;</div>
    <div class="col col-10">
        <div class="nav-left">
            <div class="tabs">
                <a {% if url == '/' %} class="active" {% endif %}href="/">Status</a>
                <a {% if url == 'filament' %} class="active" {% endif %}href="/filament">Filament</a>
                <a {% if url == 'printer' %} class="active" {% endif %} href="/printer">Printer</a>
                <a {% if url == 'wifi' %} class="active" {% endif %} href="/wifi">WiFi</a>
            </div>
        </div>
        <div class="row is-center">
            {% if mqtt_error %}
                <div class="col col4 is-center">
                    <div class="card bd-error">
                        <header><h4>MQTT Error</h4></header>
                        <p>
                            {% if mqtt_error == "1" %}Invalid protocol version
                            {% elif mqtt_error == "2" %}Client ID rejected
                            {% elif mqtt_error == "3" %}Server unavailable
                            {% elif mqtt_error == "4" %}Bad username or password
                            {% elif mqtt_error == "5" %}Not authorized
                            {% else %}Unknown error code: {{mqtt_error}}
                            {% endif %}
                        </p>
                    </div>
                </div>
            {% endif %}
            {% if wifi_error %}
                <div class="col col4 is-center">
                    <div class="card bd-error">
                        <header><h4>WiFi Error</h4></header>
                        <p>{{wifi_error}}</p>
                    </div>
                </div>
            {% endif %}
        </div>
