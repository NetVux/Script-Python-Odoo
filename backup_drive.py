import requests
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def authenticate_gdrive_service_account(credentials_path):
    """Autenticación con una cuenta de servicio de Google Drive."""
    credentials = service_account.Credentials.from_service_account_file(
        os.path.join(credentials_path, 'credentials.json'),
        scopes=['https://www.googleapis.com/auth/drive']
    )
    service = build('drive', 'v3', credentials=credentials)
    return service

def backup_odoo_and_upload_to_drive(odoo_server, master_password, db_name, gdrive_folder_id, credentials_path, max_backups):
    """
    Realiza un respaldo de Odoo y lo sube a Google Drive.

    :param odoo_server: URL del servidor Odoo (e.g., http://localhost:8069)
    :param master_password: Contraseña maestra del servidor Odoo
    :param db_name: Nombre de la base de datos a respaldar
    :param gdrive_folder_id: ID de la carpeta de Google Drive donde se subirá el respaldo
    :param credentials_path: Ruta donde se encuentran las credenciales de Google Drive
    :param max_backups: Cantidad máxima de respaldos a mantener en Google Drive
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file_path = f"/tmp/{db_name}_backup_{timestamp}.zip"
    backup_url = f"{odoo_server}/web/database/backup"

    # Paso 1: Realizar el respaldo de Odoo
    try:
        response = requests.post(
            backup_url,
            data={
                'master_pwd': master_password,
                'name': db_name,
                'backup_format': 'zip',
            },
            stream=True
        )
        response.raise_for_status()

        with open(backup_file_path, 'wb') as backup_file:
            for chunk in response.iter_content(chunk_size=8192):
                backup_file.write(chunk)

        print(f"Respaldo de Odoo guardado en {backup_file_path}")
    except Exception as e:
        print(f"Error al realizar el respaldo de Odoo: {e}")
        return

    # Paso 2: Subir el respaldo a Google Drive
    try:
        drive_service = authenticate_gdrive_service_account(credentials_path)

        file_metadata = {
            'name': os.path.basename(backup_file_path),
            'parents': [gdrive_folder_id]
        }
        media = MediaFileUpload(backup_file_path, mimetype='application/zip')

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f"Respaldo subido a Google Drive con éxito: {file.get('id')}")

        # Paso 3: Obtener la lista de archivos en la carpeta de Google Drive
        results = drive_service.files().list(
            q=f"'{gdrive_folder_id}' in parents and mimeType='application/zip'",
            spaces='drive',
            fields='files(id, name, createdTime)',
            orderBy='createdTime'
        ).execute()

        items = results.get('files', [])

        # Imprimir todos los archivos en la carpeta de Google Drive
        print("Archivos en la carpeta de Google Drive:")
        for item in items:
            print(f"Nombre: {item['name']}, Fecha de creación: {item['createdTime']}")

        # Paso 4: Eliminar respaldos antiguos si se excede la cantidad máxima
        if len(items) > max_backups:
            items.sort(key=lambda x: x['createdTime'])
            for item in items[:-max_backups]:
                drive_service.files().delete(fileId=item['id']).execute()
                print(f"Respaldo antiguo eliminado: {item['name']}")

    except Exception as e:
        print(f"Error al subir el respaldo a Google Drive: {e}")
    finally:
        # Eliminar el archivo local solo si existe
        if os.path.exists(backup_file_path):
            os.remove(backup_file_path)

if __name__ == "__main__":
    # Variables del servidor Odoo
    ODOO_SERVER = "http://172.21.50.164:1769"
    MASTER_PASSWORD = "admin1"
    DB_NAME = "adel"

    # ID de la carpeta de Google Drive donde se subirá el respaldo
    GDRIVE_FOLDER_ID = "1pBt4P8su44eVBD_lm8l7o8s_uYjSalQb"

    # Ruta de las credenciales de Google Drive
    CREDENTIALS_PATH = "/opt"

    # Cantidad máxima de respaldos a mantener
    MAX_BACKUPS = 2

    backup_odoo_and_upload_to_drive(ODOO_SERVER, MASTER_PASSWORD, DB_NAME, GDRIVE_FOLDER_ID, CREDENTIALS_PATH, MAX_BACKUPS)