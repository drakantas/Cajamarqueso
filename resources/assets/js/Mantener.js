(function ($) {
    'use strict';

    class Mantener
    {
        constructor(name, wrapper, search_href, search_input, search_submit, search_results, search_results_flag)
        {
            this.name = name;
            this.results_wrapper = wrapper;
            this.search = {
                href: search_href,
                input: search_input,
                submit: search_submit,
                results: search_results,
            }
        }

        initialize()
        {
            this.setResultOnClickEvent();
            this.results_wrapper.append(this.modal());
            this.setBtnOnClickEvent();
            this.setSearchEvents();
            this.setSelectSearchResultEvent();
            this.setLoadMoreEvent();
        }

        getSelected()
        {
            var selected = this.results_wrapper.find('.result.selected').get(0);

            if (typeof selected === 'undefined') {
                return null;
            }

            return $(selected);
        }

        setResultOnClickEvent()
        {
            $(document).on('click', '.result', (event) => {
                var _s = this.getSelected();

                if (_s === null) {
                    $(event.currentTarget).addClass('selected');
                    return;
                }

                _s.removeClass('selected');
                $(event.currentTarget).addClass('selected');
            });
        }

        setBtnOnClickEvent()
        {
            var search_btn, register_btn, update_btn, remove_btn;

            search_btn = this.results_wrapper.find('.search_btn').get(0);
            update_btn = this.results_wrapper.find('.update_btn').get(0);
            remove_btn = this.results_wrapper.find('.remove_btn').get(0);

            if (typeof search_btn === 'undefined') {
                search_btn = null;
            }
            else {
                search_btn = $(search_btn);
            }

            if (typeof update_btn === 'undefined') {
                update_btn = null;
            }
            else {
                update_btn = $(update_btn);
            }

            if (typeof remove_btn === 'undefined') {
                remove_btn = null;
            }
            else {
                remove_btn = $(remove_btn);
            }

            this.setBtnEvent(search_btn, true);
            this.setBtnEvent(update_btn);
            this.setBtnEvent(remove_btn);
        }

        setBtnEvent(btn, search_flag = false)
        {
            if (btn === null) {
                return;
            }

            btn.on('click', (event) => {
                event.preventDefault();

                if (search_flag === true) {
                    $('#mantener-buscar').modal('show');
                    return;
                }

                var _s = this.getSelected();

                if (_s === null) {
                    $('#mantener_error .contenido_error').html('Debes de seleccionar un ' + this.name + ' primero.');
                    $('#mantener_error').modal('show');

                    setTimeout(() => {
                        $('#mantener_error').modal('hide');
                    }, 1500);

                    return;
                }

                var route = btn.attr('href') + '/' + $.trim(_s.find('div:first').html());

                window.location.href = route;
            });
        }

        setSearchEvents()
        {
            $(this.search.submit).on('click', (event) => {
                var _val = $.trim($(this.search.input).val());
                if (_val === null || _val === '' || _val === ' ') {
                    this.showSearchError('Debes llenar el campo de ' + $(this.search.input).attr('name') + '.');
                    return;
                }

                var _route = this.search.href + '/' + $(this.search.input).val().replace(' ', '-')
                $.ajax(_route, {
                    type: 'POST',
                    context: this,
                    dataType: 'json',
                    beforeSend: () => {
                        $(this.search.submit).button('loading');
                    },
                    success: (response) => {
                        var results = JSON.parse(response);

                        if (results[0] == null) {
                            this.showSearchError('No se encontró ningún ' + this.name + '.', true)
                            return;
                        }

                        $(this.search.results).html('');

                        $.each(results, (k, v) => {
                            var result = results[k];
                            this.showResult(result);
                        });

                        this.showResultButtons();
                    },
                    error: () => {
                        this.showSearchError('No se encontró ningún ' + this.name + '.', true);
                    },
                    complete: () => {
                        $(this.search.submit).button('reset');
                    }
                });
            });
        }

        setSelectSearchResultEvent()
        {
            $(document).on('click', '.mantener_buscar_btns_wrapper .btn', (event) => {
                event.preventDefault();

                var _selected = $(this.search.results).find('input[type="radio"]:checked');

                if (typeof _selected.get(0) === 'undefined') {
                    this.showSearchError('Debe seleccionar uno de los resultados.');
                    return;
                }

                window.location.href = $(event.currentTarget).attr('href') + '/' + _selected.attr('value');
            });
        }

        setLoadMoreEvent()
        {
            var load_more_btn = $(this.results_wrapper).find('.load_more');

            load_more_btn.on('click', (event) => {
                event.preventDefault();

                var pagina = parseInt(load_more_btn.data('pagina'));
                var href = load_more_btn.attr('href');
                var route = href + '/' + pagina;

                $.ajax(route, {
                    type: 'GET',
                    context: this,
                    dataType: 'json',
                    beforeSend: () => {
                        load_more_btn.button('loading');
                    },
                    success: (response) => {
                        load_more_btn.data('pagina', '' + (pagina + 1));

                        var results = JSON.parse(response);
                        var results_list = this.results_wrapper.find('.mantenimiento_lista');

                        if (typeof results[0] === 'undefined') {
                            load_more_btn.addClass('disabled');
                            load_more_btn.html('No se encontraron más resultados.');
                            return;
                        }
                        console.log(results);

                        for (var i = 0; i < results.length; i++) {
                            var result = results[i];
                            var _dom = '<div class="col-md-12 result">';
                            $.each(result, (k, v) => {
                                _dom += '<div class="col-sm-2 r-col">';
                                _dom += `${v}`;
                                _dom += '</div>';
                            });
                            _dom += '</div>';
                            results_list.append(_dom);
                        }

                        load_more_btn.button('reset');
                    }
                });


            });
        }

        showResultButtons() {
            var _btn = $(this.results_wrapper).find('.buttons-wrapper').clone(true).removeClass('text-right');
            var _dom = '<div class="row"><div class="col-sm-12 mantener_buscar_btns_wrapper text-center"></div></div>';

            _btn.find('.btn:first').remove();
            _btn.find('.btn:first').remove();

            _btn.find('.btn').off('click');

            $(this.search.results).append(_dom);
            $('.mantener_buscar_btns_wrapper').html(_btn);
        }

        showResult(result) {
            var first = true;
            var _dom = '<label><input type="radio" name="';

            $.each(result, (k, v) => {
                if (first) {
                    _dom += k;
                    _dom += `" value="${v}"> `;
                    first = false;
                    return;
                }
                _dom += `${v} `;
            });

            _dom = $.trim(_dom);

            $(this.search.results).append(_dom + '</label><br>');
        }

        showSearchError(error, flag = false) {
            var _error = `<div class="col-sm-12" style="padding-top:10px;"><div class="alert alert-danger" role="alert">${error}</div></div>`;

            if (!flag) {
                $('#mantener-buscar').find('.alert').parent().remove();
                $(this.search.results).prepend(_error);
                return;
            }

            $(this.search.results).html(_error);
        }

        modal(error)
        {
            return `<div class="modal fade" id="mantener_error" tabindex="-1" role="dialog" aria-labelledby="mantener_error">
                        <div class="modal-dialog modal-sm" role="document">
                            <div class="modal-content">
                                <div class="modal-body contenido_error">
                                </div>
                            </div>
                        </div>
                    </div>`;
        }
    }

    function Plugin(name, search_href, search_input, search_submit, search_results)
    {
        var _mantener = new Mantener(name, this, search_href, search_input, search_submit, search_results);
        _mantener.initialize();
    }

    $.fn.mantener = Plugin;
})(jQuery);
