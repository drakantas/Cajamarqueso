class Pedido
{
    constructor(routes, selectors)
    {
        this.routes = routes;
        this.selectors = selectors;
        this.vanillaSelectors = $.extend({}, selectors);

        $.map(this.selectors, (value, key) => {
            this.selectors[key] = $(value);
        });
    }

    initialize()
    {
        this.selectors['buscar-cliente'].find('#search').on('click', () => {
            this.poll();
        });

        this.addClickEventToProducts();

        this.addNewProductEvent();

        this.addTotalPriceEvent();

        this.addRemoveProductEvent();
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

        if (results[0] == null) {
            this.showAlert();
            return;
        }

        results_dom = `<hr><div class="col-sm-12">
            <form class="search-results" method="post" action="${this.routes['nuevo-pedido']}">`;

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
            </form>
        </div>`;

        this.selectors['buscar-cliente'].find('.modal-body .search_results').html(results_dom);
    }

    showAlert()
    {
        var alert = `<hr>
            <div class="col-sm-12">
                <div class="alert alert-danger" role="alert">
                    No se encontró a ningún cliente.
                </div>
            </div>`;

        this.selectors['buscar-cliente'].find('.modal-body .search_results').html(alert);
    }

    selectedProduct()
    {
        var selected = this.selectors['lista-productos'].find('.product').find('label.selected').get(0);

        if (typeof selected === 'undefined') {
            return null;
        }

        return $(this.selectors['lista-productos'].find('.product').find('label.selected').get(0));
    }

    addClickEventToProducts()
    {
        var productos = this.selectors['lista-productos'].find('.product').find('label');

        productos.on('click', (event) => {
            var selected = this.selectedProduct();
            var producto = $(event.currentTarget);

            if (selected === producto) {
                return;
            }

            if (selected !== null) {
                selected.removeClass('selected');
            }

            producto.addClass('selected');
        });
    }

    addNewProductEvent()
    {
        this.selectors['agregar-producto'].on('click', () => {
            var producto = this.selectedProduct();

            if (producto === null) {
                return;
            }

            var producto_id = producto.prev().attr('value');
            var producto_nombre = producto.find('.product_name').html();
            var producto_stock = producto.find('.product_stock').html();

            var producto_carrito = this.selectors['carrito'].find('.product label:contains("'+producto_nombre+'")');

            if (typeof producto_carrito.html() === 'undefined') {
                this.selectors['carrito'].append(this.buildProductDom(producto_id, producto_nombre, producto_stock));
                return;
            }

            producto_carrito.next().next().focus();
        });
    }

    buildProductDom(id, name, stock)
    {
        return `
            <div class="panel panel-default product">
                <div class="panel-body">
                    <div class="col-md-3 text-center">
                        <button type="button" class="btn btn-danger remove_product">
                            <span class="glyphicon glyphicon-minus" aria-hidden="true"></span>
                        </button>
                    </div>
                    <div class="col-md-9">
                        <label for="producto_${id}" class="selected_product_name">${name}</label><br>
                        <input type="text" class="form-control" id="producto_${id}" name="producto_${id}" placeholder="Stock: ${stock}">
                    </div>
                </div>
            </div>`;
    }

    updateTotalAmount()
    {
        var productos = this.selectors['carrito'].find('.product');

        var monto_total = 0.0;

        for (var i = 0; i < productos.length; i++) {
            producto = $(productos[i]);

            var selector_producto = this.selectors['lista-productos'].find('.product:contains("'+producto.find('label').html()+'")');
            var precio_producto = parseFloat(selector_producto.find('.product_price').html());
            var cantidad_producto = producto.find('input[type="text"]').val();


            if (cantidad_producto === '') {
                cantidad_producto = 0;
            } else {
                if (!/^\d+$/.test(cantidad_producto)) {
                    cantidad_producto = 0;
                } else {
                    cantidad_producto = parseInt(cantidad_producto);
                }
            }

            monto_total += precio_producto * cantidad_producto;
        }

        this.selectors['monto-total'].html('' + monto_total.toFixed(2));
    }

    addTotalPriceEvent()
    {
        $(document).on('change paste', this.vanillaSelectors['carrito'] + ' .product input[type="text"]', () => {
            this.updateTotalAmount();
        });
    }

    addRemoveProductEvent()
    {
        $(document).on('click', this.vanillaSelectors['carrito'] + ' .product .remove_product', (event) => {

            $(event.currentTarget).parent().parent().parent().remove();

            this.updateTotalAmount();
        });
    }
}


let pedido = new Pedido({
    'buscar-cliente': '/buscar-cliente',
    'nuevo-pedido': '/pedido/nuevo'
}, {
    'buscar-cliente': '#buscar-cliente',
    'lista-productos': '#products-list',
    'agregar-producto': '#agregar-producto',
    'carrito': '.selected-products',
    'monto-total': '.monto_total'
});
pedido.initialize();
