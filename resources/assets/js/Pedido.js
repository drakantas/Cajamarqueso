class Pedido
{
    constructor(routes, selectors)
    {
        this.routes = routes;
        this.selectors = selectors;

        Object.keys(this.selectors).map((key, index) => {
            this.selectors[key] = $(this.selectors[key]);
        });
    }

    initialize()
    {
        this.selectors['buscar-cliente'].find('#search').on('click', () => {
            this.poll();
        });
    }

    grabData()
    {
        var [search_type, search_query] = [this.selectors['buscar-cliente'].find('#search_type'),
                                           this.selectors['buscar-cliente'].find('#search_query')];

        return [search_type.find(':selected').val(), search_query.val().split(' ').join('-')];
    }

    poll()
    {
        var data = this.grabData();
        var route = this.routes['buscar-cliente'] + `/${data[0]}/${data[1]}`;

        $.ajax(route, {
            type: 'POST',
            context: this,
            dataType: 'json',
            beforeSend: () => {
                this.selectors['buscar-cliente'].find('#search').button('loading');
            },
            success: (response) => {
                this.showResults(response);
            },
            complete: () => {
                this.selectors['buscar-cliente'].find('#search').button('reset');
            }
        });
    }

    showResults(results)
    {
        results = JSON.parse(results);
        console.log(results);
        if (results[0] == null) {
            this.showAlert();
            return;
        }

        results_dom = `<form class="search-results" method="post" action="${this.routes['nuevo-pedido']}">`;

        for (var i = 0; i < results.length; i++) {
            var result = results[i];
            var result_dom = `
                <div class="radio">
                    <label>
                        <input type="radio" name="id_cliente" value="${result['id_cliente']}"> ${result['nombre_cliente']}
                    </label>
                </div>`;
            results_dom = results_dom + result_dom;
        }

        results_dom = `${results_dom}
            <div class="text-center">
                <button type="submit" class="btn btn-primary">
                    Seleccionar cliente
                </button>
            </div>
        </form>`;

        this.selectors['buscar-cliente'].find('.modal-body').append(results_dom);
    }

    showAlert()
    {
        var alert = `
            <div class="alert alert-danger" role="alert">
                No se encontró a ningún cliente.
            </div>`;

        this.selectors['buscar-cliente'].find('.modal-body').append(alert);
    }
}


let pedido = new Pedido({
    'buscar-cliente': '/buscar-cliente',
    'nuevo-pedido': '/pedido/nuevo'
}, {
    'buscar-cliente': '#buscar-cliente'
});
pedido.initialize();
