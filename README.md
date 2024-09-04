# Kreditos

Una aplicación para la gestión de deudas, en este repositorio se ha implementado el backend de la aplicación. 

## Instalación del servidor

El servidor en su totalidad fue desarrollado en Python con los frameworks **SQLAlchemy** y **FastAPI**, lo que provee gran versatilidad y rapidez en el despliegue y en la face de producción.

### Pasos para la instalación
1. Instalación del interprete Python en su versión 3.12.3 o superior
2. Instalación del entorno virtual para desarrollo
    ```
    python -m venv .venv
    ```
    Debemos verificar que estamos dentro del entorno virtual, en muchos casos aparece ".env" al inicio de la consola, en caso de no ser asi, lo activamos.
    
    Entramos a la carpeta .venv/Scripts/ y ejecutamos el script activate.bat
3. Instalación de todos los paquetes requeridos para su funcionamiento:
    ```
    python -m pip install -r requirements.txt
    ```    
4. Ejecutamos el proyecto
    ```
    python main.py 
    ``` 

5. Revisamos el puerto de escucha para el servidor, en el fichero main.py, en la linea 124 cambiamos el puerto 8080 por otro. Esto permitira la co-existencia del servidor con otras versiones.

### Bases de Datos 

- Al desplegar el proyecto debemos tener previamente el servicio de posgres ejecutandose y la base de datos creada. La base de datos postgres se encuentra en la raiz del proyecto y esta en formato SQL.

- La configuración de la conexión de la base de datos se encuentra en la carpeta database\database.py. Se encuentra en formato URI, el cual debemos tener cuidado al editarlo.

- El nombre de la base de datos en el entorno de desarrollo: **debtmanager**

    ```
    engine = create_engine('postgresql+psycopg2://<user>:<password>@<host>/<database_name>')
    ```

