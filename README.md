# Script-Python-Odoo

Este script se usa para crear backups automáticos de Odoo y subirlos a una carpeta de Google Drive utilizando una cuenta de servicio de Google Console.

## Requisitos

1. Crear credenciales JSON de Google y guardarlas en una ubicación accesible.
2. Configurar las siguientes variables en el script:

    ```python
    # Variables del servidor Odoo
    ODOO_SERVER = "http://172.21.50.164:1769"
    MASTER_PASSWORD = "admin1"
    DB_NAME = "NetVux"

    # ID de la carpeta de Google Drive donde se subirá el respaldo
    GDRIVE_FOLDER_ID = "1pBt4P8su44eVBD_lm8l7o8s_uYjSalQb"

    # Ruta de las credenciales de Google Drive
    CREDENTIALS_PATH = "/opt"

    # Cantidad máxima de respaldos a mantener
    MAX_BACKUPS = 2
    ```

## Ejecución

Para ejecutar el script diariamente, puedes usar `crontab`. Por ejemplo, para ejecutarlo todos los días a las 2 AM, añade la siguiente línea a tu crontab:

```sh
0 2 * * * /usr/bin/python3 /ruta/al/script.py