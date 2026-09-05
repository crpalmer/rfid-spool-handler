{% args model %}
{% set printer = model.printer %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'printer', model %}
    <h1>Printer Setup</h1>
    <div class="form-container">
        <form action="#" method="post">
            <label for="ip">IP Address</label>
            <input id="ip" name="ip" type="text" size="20" pattern="[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}" placeholder="xxx.xxx.xxx.xxx" required value="{[printer["ip"]]}" />
            <label for="serial">Serial #</label>
            <input id="serial" name="serial" type="text" size="20" placeholder="xxxxxxxxxxxxxxx" value="{[printer["serial"]]}" />
            <label for="ac">Access Code</label>
            <input id="ac" name="ac" type="text" size="20" pattern="[0-9a-fA-F]{8}" placeholder="xxxxxxxx" required value="{[printer["ac"]]}" />
            <p>&nbsp;</p>
            <button type="submit">Save</button>
        </form>
    </div>
{% include "body-end.tpl" %}
</body>
</html>
