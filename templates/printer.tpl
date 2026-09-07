{% args model %}
<html>
{% include "head.partial" %}
<body>
{% include "body-start.tpl" 'printer', model %}
    <h1>Printers</h1>
    <b>
        <div class="row">
            <div class="col col-1">&nbsp;</div>
            <div class="col col-2">Name</div>
            <div class="col col-1">IP Address</div>
            <div class="col col-2">Serial #</div>
            <div class="col col-1">Access Code</div>
        </div>
    </b>
{% for (id, printer) in sorted(model.get_printers().items(), key=lambda i: (i[1].get("name", "").upper(), i[1].get("ip"))) %}
    <div class="row">
        <div class="col col-1">{[id]}</div>
        <div class="col col-2">{[printer.get("name")]}</div>
        <div class="col col-1">{[printer.get("ip")]}</div>
        <div class="col col-2">{[printer.get("serial")]}</div>
        <div class="col col-1">{[printer.get("ac")]}</div>
        <div class="col col-2">
            <a href="/printer/edit?id={[id]}">edit</a>&nbsp;
            <a href="/printer/delete?id={[id]}">delete</a>
        </div>
    </div>
{% endfor %}
    <form action="/printer/add">
        <button type="submit">Add Printer</button>
    </form>
{% include "body-end.tpl" %}
</body>
</html>
