class Pedido
{
    constructor(routes)
    {
        this.routes = routes;
    }

    initialize()
    {
        alert(this.routes);
    }
}


let pedido = new Pedido('xd');
pedido.initialize();
