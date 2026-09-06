{% args action, model, id=None %}
{% set printer = model.get_printers().get(id, {}) %}
    <div class="form-container">
        <form action="{[action]}" method="post">
            <input name="id" type="hidden" value="{[id]}"/>
            <label for="name">Name</label>
            <input id="name" name="name" type="text" require value="{[printer.get("name", "")]}"/>
            <label for="ip">IP Address</label>
            <input id="ip" name="ip" type="text" size="20" pattern="[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}" placeholder="xxx.xxx.xxx.xxx" required value="{[printer.get("ip", "")]}" />
            <label for="serial">Serial #</label>
            <input id="serial" name="serial" type="text" size="20" placeholder="xxxxxxxxxxxxxxx" value="{[printer.get("serial", "")]}" />
            <label for="ac">Access Code</label>
            <input id="ac" name="ac" type="text" size="20" pattern="[0-9a-fA-F]{8}" placeholder="xxxxxxxx" required value="{[printer.get("ac", "")]}" />
            <p>&nbsp;</p>
            <button type="submit">Save</button>
        </form>
        <form action="/printer">
            <button type="submit">Cancel</button>
        </form>
    </div>