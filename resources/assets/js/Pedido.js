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
            this.poll(this.selectors['buscar-cliente'], '#search', this.routes['nuevo-pedido'],
                     ['#search_type', '#search_query'], '.search_results_2');
        });

        this.addClickEventToProducts();

        this.addNewProductEvent();

        this.addTotalPriceEvent();

        this.addRemoveProductEvent();

        this.setSearchOrderEvent();

        this.setSearchResultsEvent();

        this.setResultOptionsEvents();

        this.updateTotalAmount();

        this.setBtnSearchEvent(['buscar-pedido', 'buscar-cliente'], ['.search_results', '.search_results_2']);
    }

    setBtnSearchEvent(bad_variable, bad_variable_2)
    {
        $(document).on('click', bad_variable_2[0] + ' ' + this.vanillaSelectors['btn-seleccionar-cliente'], (event) => {
            var _selected_1 = this.selectors[bad_variable[0]].find(bad_variable_2[0]).find(':checked');
            if (typeof _selected_1.get(0) === 'undefined') {
                event.preventDefault();
                this.showAlert(this.selectors[bad_variable[0]], 'Debes de seleccionar un cliente.', bad_variable_2[0], true);
            }
        });
        $(document).on('click', bad_variable_2[1] + ' ' + this.vanillaSelectors['btn-seleccionar-cliente'], (event) => {
            var _selected_2 = this.selectors[bad_variable[1]].find(bad_variable_2[1]).find(':checked');
            if (typeof _selected_2.get(0) === 'undefined') {
                event.preventDefault();
                this.showAlert(this.selectors[bad_variable[1]], 'Debes de seleccionar un cliente.', bad_variable_2[1], true);
            }
        });
    }

    grabData(selector, input)
    {
        var [search_type, search_query] = [selector.find(input[0]),
                                           selector.find(input[1])];

        return [search_type.find(':selected').val(), search_query.val().split(' ').join('-')];
    }

    poll(selector, trigger, action, input, r_wrapper)
    {
        var data = this.grabData(selector, input);
        var route = this.routes['buscar-cliente'] + `/${data[0]}/${data[1]}`;

        if (data[1] == '') {
            this.showAlert(selector, 'Debes de llenar el campo de búsqueda.', r_wrapper);
            return;
        }

        $.ajax(route, {
            type: 'POST',
            context: this,
            dataType: 'json',
            beforeSend: () => {
                selector.find(trigger).button('loading');
            },
            success: (response) => {
                this.showResults(selector, response, action, r_wrapper);
            },
            complete: () => {
                selector.find(trigger).button('reset');
            }
        });
    }

    showResults(selector, results, action, r_wrapper)
    {
        results = JSON.parse(results);

        if (results[0] == null) {
            this.showAlert(selector, 'No se encontró a ningún cliente.', r_wrapper);
            return;
        }

        results_dom = `<hr><div class="col-sm-12">
            <form class="search-results" method="post" action="${action}">`;

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
                    <button type="submit" class="btn btn-primary" id="busqueda-seleccionar-cliente">
                        Seleccionar cliente
                    </button>
                </div>
            </form>
        </div>`;

        selector.find('.modal-body ' + r_wrapper).html(results_dom);
    }

    showAlert(selector, alert_message, r_wrapper, flag = false)
    {
        var alert = `
            <div class="col-sm-12" style="margin-top:10px;">
                <div class="alert alert-danger" role="alert">
                    ${alert_message}
                </div>
            </div>`;

        var _a = selector.find('.modal-body ' + r_wrapper).find('.alert');

        if (!flag) {
            selector.find('.modal-body ' + r_wrapper).html(alert);
            return;
        }
        else {
            _a.parent().remove();
            selector.find('.modal-body ' + r_wrapper).prepend(alert);
        }
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
        this.selectors['agregar-producto'].on('click', (event) => {
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

            producto_carrito.next().next().find('input[type="text"]').focus();
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
                        <div class="input-group">
                            <input type="text" class="form-control" id="producto_${id}" name="producto_${id}" placeholder="Stock: ${stock}">
                            <div class="input-group-addon sub_total">S/. 0.00</div>
                        </div>
                    </div>
                </div>
            </div>`;
    }

    updateTotalAmount()
    {
        var productos = this.selectors['carrito'].find('.product');

        var monto_total = 0.0, subtotal = 0.0, igv = 0.0;

        for (var i = 0; i < productos.length; i++) {
            producto = $(productos[i]);

            var selector_producto = this.selectors['lista-productos'].find('.product:contains("'+producto.find('label').html()+'")');
            var precio_producto = parseFloat(selector_producto.find('.product_price').html());
            var cantidad_producto = producto.find('input[type="text"]').val();
            var subtotal_producto = producto.find('.sub_total');

            if (cantidad_producto === '') {
                cantidad_producto = 0;
            } else {
                if (!/^\d+$/.test(cantidad_producto)) {
                    cantidad_producto = 0;
                } else {
                    cantidad_producto = parseInt(cantidad_producto);
                }
            }

            var _subtotal_producto = precio_producto * cantidad_producto;
            subtotal_producto.html('S/. ' + _subtotal_producto.toFixed(2));
            monto_total += _subtotal_producto;
        }

        igv = monto_total * 0.18;
        subtotal = monto_total - igv;

        this.selectors['igv'].html('' + igv.toFixed(2));
        this.selectors['subtotal'].html('' + subtotal.toFixed(2));
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

    setSearchOrderEvent()
    {
        $('a[href$="/pedido/pago"], a[href$="/pedido/actualizar"]').on('click', (event) => {
            // No realizar la redirección
            event.preventDefault();

            // Mostrar modal de búsqueda de pedido
            this.selectors['buscar-pedido'].modal('show');
        });

        this.selectors['buscar-pedido'].find('#o_search').on('click', () => {
            this.poll(this.selectors['buscar-pedido'], '#o_search', this.routes['pedidos'],
                     ['#o_search_type', '#o_search_query'], '.search_results');
        });
    }

    setSearchResultsEvent()
    {
        this.selectors['resultado-pedido'].on('click', (event) => {
            var _s = $(event.currentTarget);
            var _a = this.getSelectedResult();

            if (_a === null) {
                _s.addClass('selected');
                return;
            }
            else if(_a === _s) {
                return;
            }

            _a.removeClass('selected');
            _s.addClass('selected');
        });
    }

    setResultOptionsEvents()
    {
        this.selectors['registrar-pago'].on('click', () => {
            var pedido_id = this.validateSelectedOrder();
            if (pedido_id !== null) {
                if($('.order.selected .estado_pedido').html() === 'Pagado') {
                    $('#error_pedido_ya_pagado').modal('show');
                    setTimeout(() => {
                        $('#error_pedido_ya_pagado').modal('hide');
                    }, 1500);
                }
                else {
                    window.location.replace(this.routes['registrar-pago'] + `/${pedido_id}`);
                }
            } else {
                $('#error_no_selecciono_pedido').modal('show');
                setTimeout(() => {
                    $('#error_no_selecciono_pedido').modal('hide');
                }, 1500);
            }
        });

        this.selectors['actualizar-pedido'].on('click', () => {
            var pedido_id = this.validateSelectedOrder();
            if (pedido_id !== null) {
                window.location.replace(this.routes['actualizar-pedido'] + `/${pedido_id}`);
            } else {
                $('#error_no_selecciono_pedido').modal('show');
                setTimeout(() => {
                    $('#error_no_selecciono_pedido').modal('hide');
                }, 1500);
            }
        });
    }

    validateSelectedOrder()
    {
        var selected = this.getSelectedResult();

        if (selected === null) {
            return null;
        }

        return selected.data('pedido-id');
    }

    getSelectedResult()
    {
        var active = $(this.vanillaSelectors['resultado-pedido']+'.selected').get(0);

        if (typeof active === 'undefined') {
            return null;
        }

        return $(active);
    }
}


let pedido = new Pedido({
    'buscar-cliente': '/buscar-cliente',
    'nuevo-pedido': '/pedido/nuevo',
    'pedidos': '/pedidos',
    'registrar-pago': '/pedido/registrar-pago',
    'actualizar-pedido': '/pedido/actualizar'
}, {
    'buscar-cliente': '#buscar-cliente',
    'lista-productos': '#products-list',
    'agregar-producto': '#agregar-producto',
    'carrito': '.selected-products',
    'monto-total': '.monto_total',
    'subtotal': '.subtotal',
    'igv': '.igv',
    'buscar-pedido': '#buscar-pedido',
    'resultado-pedido': '.client-orders .order',
    'registrar-pago': '#registrar-pago',
    'actualizar-pedido': '#actualizar-pedido',
    'btn-seleccionar-cliente': '#busqueda-seleccionar-cliente'
});
pedido.initialize();
