import datetime
import pytz
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import requests


def fecha_peru_hoy():
    lima_timezone = pytz.timezone('America/Lima')
    lima_time = datetime.datetime.now(lima_timezone)
    return lima_time.date()

def autenticar_drive():
    gauth = GoogleAuth()
    # Intenta cargar las credenciales almacenadas
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Autenticación si no hay credenciales guardadas
        gauth.LocalWebserverAuth()  # Esto abre un navegador para autorizar la app
        gauth.SaveCredentialsFile("mycreds.txt") 
    elif not gauth.credentials or gauth.access_token_expired:
        if gauth.access_token_expired:
            print("Access token expired. Refreshing...")
        # Solicitar acceso offline para obtener un refresh token
            gauth.LocalWebserverAuth()  # No es necesario el parámetro 'access_type'
            gauth.SaveCredentialsFile("mycreds.txt")  # Guardar las credenciales para la próxima vez
    else:
        # Autorizar con las credenciales guardadas
        gauth.Authorize()

    # Retorna el objeto GoogleDrive con las credenciales autorizadas
    drive = GoogleDrive(gauth)
    return drive

def obtener_archivos_drive(folder_id):
    drive = autenticar_drive()
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents"}).GetList()
    archivos_descargados = []
    archivos_vistos = set()  # Evitar duplicados

    for file in file_list:
        file_name = file['title']
        file_id = file['id']
        # Verificar si es un archivo válido (CSV o Excel)
        if file_name.endswith(('.csv', '.xlsx')) and file_name not in archivos_vistos:
            print(f"Cargando archivo: {file_name}")
            file_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            try:
                file_content = requests.get(file_url).content
                archivos_descargados.append((file_name, file_content))
                archivos_vistos.add(file_name)
            except Exception as e:
                print(f"Error al descargar {file_name}: {e}")

    return archivos_descargados