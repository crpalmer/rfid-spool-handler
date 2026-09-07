{% args url, model %}
<div class="row">
    <div class="col col-1">&nbsp;</div>
    <div class="col col-10">
        <div class="nav-left">
            <div class="tabs">
                <a {% if url == '/' %} class="active" {% endif %}href="/">Status</a>
                <a {% if url == 'filament' %} class="active" {% endif %}href="/filament">Filament</a>
                <a {% if url == 'printer' %} class="active" {% endif %} href="/printer">Printers</a>
                <a {% if url == 'wifi' %} class="active" {% endif %} href="/wifi">WiFi</a>
            </div>
        </div>
        <div class="row is-center">
            {% set mqtt_error = model.get_mqtt_error() %}
            {% if len(model.mqtt_error) > 0 %}
                {% set printers = model.get_printers() %}
                <div class="col col4 is-center">
                    <div class="card bd-error">
                        <header><h4>MQTT Error</h4></header>
                        {% for (id, error) in mqtt_error.items() %}
                        <p>
                            {% set printer = printers.get(id) %}
                            {% if printer is not None %}
                                {[printer.get("name")]}:
                            {% endif %}
                            {% if error == "1" %}Invalid protocol version
                            {% elif error == "2" %}Client ID rejected
                            {% elif error == "3" %}Server unavailable
                            {% elif error == "4" %}Bad username or password
                            {% elif error == "5" %}Not authorized
                            {% else %}{[error]}
                            {% endif %}
                        </p>
                        {% endfor %}
                    </div>
                </div>
            {% endif %}
            {% set transient_error = model.get_transient_error() %}
            {% if transient_error is not None %}
                <div class="col col4 is-center">
                    <div class="card bd-error">
                        <header><h4>Error</h4></header>
                        <p>{[transient_error]}</p>
                    </div>
                </div>
            {% endif %}
            {% set rfid_error = model.get_rfid_error() %}
            {% if rfid_error is not None %}
                <div class="col col4 is-center">
                    <div class="card bd-error">
                        <header><h4>RFID Reader Error</h4></header>
                        <p>{[rfid_error]}</p>
                    </div>
                </div>
            {% endif %}
        </div>
