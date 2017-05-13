# Cajamarqueso  

Proyecto **Sistema de de Pedidos y Ventas** para el curso de ISW2.

## Configuración

En `config/` se encuentran los archivos de configuración del proyecto.

## Base de datos

Ejecutar el siguiente script para crear la base de datos, el dueño de la base de datos será la cuenta de usuario root que 
PostgreSQL proveé.

```
CREATE DATABASE cajamarqueso
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;
```