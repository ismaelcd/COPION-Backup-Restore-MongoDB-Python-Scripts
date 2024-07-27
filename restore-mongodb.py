import os
import platform
import sys
import shutil
from pymongo import MongoClient
from dotenv import load_dotenv
import json
from prettytable import PrettyTable
import time
import inquirer
from colorama import init, Fore, Style
import zipfile

# Inicializar colorama
init(autoreset=True)

# Limpiar la consola al iniciar el script
def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def print_header():
    print(Fore.CYAN + "=" * 110)
    print(Fore.CYAN + " ")
    print(Fore.CYAN + "░█████╗░░█████╗░██████╗░██╗░█████╗░███╗░░██╗  ███╗░░░███╗░█████╗░███╗░░██╗░██████╗░░█████╗░██████╗░██████╗░".center(110))
    print(Fore.CYAN + "██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗████╗░██║  ████╗░████║██╔══██╗████╗░██║██╔════╝░██╔══██╗██╔══██╗██╔══██╗".center(110))
    print(Fore.CYAN + "██║░░╚═╝██║░░██║██████╔╝██║██║░░██║██╔██╗██║  ██╔████╔██║██║░░██║██╔██╗██║██║░░██╗░██║░░██║██║░░██║██████╦╝".center(110))
    print(Fore.CYAN + "██║░░██╗██║░░██║██╔═══╝░██║██║░░██║██║╚████║  ██║╚██╔╝██║██║░░██║██║╚████║██║░░╚██╗██║░░██║██║░░██║██╔══██╗".center(110))
    print(Fore.CYAN + "╚█████╔╝╚█████╔╝██║░░░░░██║╚█████╔╝██║░╚███║  ██║░╚═╝░██║╚█████╔╝██║░╚███║╚██████╔╝╚█████╔╝██████╔╝██████╦╝".center(110))
    print(Fore.CYAN + "░╚════╝░░╚════╝░╚═╝░░░░░╚═╝░╚════╝░╚═╝░░╚══╝  ╚═╝░░░░░╚═╝░╚════╝░╚═╝░░╚══╝░╚═════╝░░╚════╝░╚═════╝░╚═════╝░".center(110))
    print(Fore.CYAN + " ")
    print(Fore.CYAN + "🅁🄴🅂🅃🄾🅁🄴".center(110))
    print(Fore.CYAN + " ")
    print(Fore.CYAN + "By Ismael Cruz".center(110))
    print(Fore.CYAN + " ")
    print(Fore.CYAN + "=" * 110)
    print(Fore.CYAN + " ")
    print(Fore.CYAN + "Para seleccionar colecciones y realizar backup, seleccione con la [Barra Espaciadora].".center(110))
    print(Fore.CYAN + "Para seleccionar todas las colecciones, presione  [TAB].".center(110))
    print(Fore.CYAN + "Para comenzar el backup, pulse [Enter].".center(110))
    print(Fore.CYAN + "=" * 110)
    print(Fore.CYAN + " ")

clear_console()
print_header()

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener las variables de entorno correctas
MONGO_URI = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("MONGODB_DB")

# Comprobación de las variables de entorno
if MONGO_URI is None:
    raise ValueError("MONGO_URI no está definida en el archivo .env")
if DB_NAME is None:
    raise ValueError("DB_NAME no está definida en el archivo .env")

# Crear conexión con la base de datos
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Obtener la carpeta de backups
backup_dir = "backups-mongodb"

# Verificar que la carpeta de backups exista
if not os.path.exists(backup_dir):
    raise ValueError(f"La carpeta de backups '{backup_dir}' no existe")

# Recorrer todas las carpetas y subcarpetas para encontrar archivos ZIP
backup_files = {}
for root, dirs, files in os.walk(backup_dir):
    for file in files:
        if file.endswith('.zip'):
            collection_name = os.path.basename(root)
            if collection_name not in backup_files:
                backup_files[collection_name] = []
            backup_files[collection_name].append(os.path.join(root, file))

# Obtener todas las colecciones disponibles para restaurar y ordenarlas alfabéticamente
collections = sorted(backup_files.keys())

# Preguntar al usuario qué colecciones desea restaurar
questions = [
    inquirer.Checkbox('collections',
                      message="Seleccione las colecciones que desea restaurar",
                      choices=collections)
]

answers = inquirer.prompt(questions)
selected_collections = answers['collections']

# Preguntar si se desea sobrescribir si la colección ya existe en la base de datos
overwrite_questions = []
for collection in selected_collections:
    if collection in db.list_collection_names():
        overwrite_questions.append(
            inquirer.Confirm(f'overwrite_{collection}',
                             message=f"La colección '{collection}' ya existe en la base de datos. ¿Desea sobrescribirla?",
                             default=False)
        )

overwrite_answers = inquirer.prompt(overwrite_questions)

# Filtrar colecciones que no se desean sobrescribir y ordenarlas alfabéticamente
final_collections = []
collections_to_overwrite = []
for collection in selected_collections:
    if collection in db.list_collection_names():
        if overwrite_answers.get(f'overwrite_{collection}', True):
            collections_to_overwrite.append(collection)
        else:
            continue
    final_collections.append(collection)

final_collections.sort()

# Inicializar el estado de las colecciones
collection_status = {col: "" for col in final_collections}

# Función para imprimir la tabla de progreso con el rótulo
def print_progress_table():
    clear_console()
    print_header()

    table = PrettyTable()
    table.field_names = ["Colección", "Estado"]
    table.align["Colección"] = "l"
    table.align["Estado"] = "l"
    
    max_collection_name_length = 50  # Ajustar el máximo para nombres de colección
    max_status_length = 58  # Ajustar el máximo para el estado para que se ajuste a 110 caracteres en total

    for col, status in collection_status.items():
        truncated_col = col[:max_collection_name_length]
        truncated_status = status[:max_status_length]

        # Aplicar colores según el estado
        if "Procesando" in status:
            truncated_status = Fore.YELLOW + truncated_status + Style.RESET_ALL
        elif "Restaurada" in status:
            truncated_status = Fore.GREEN + truncated_status + Style.RESET_ALL
        else:
            truncated_status = Fore.WHITE + truncated_status + Style.RESET_ALL

        table.add_row([truncated_col, truncated_status])
    table._max_width = {"Colección": max_collection_name_length, "Estado": max_status_length}
    table.min_table_width = 110
    print(table)
    print("\n")

# Función para restaurar una colección desde archivos ZIP
def restore_collection_from_zip(collection_name, zip_files):
    collection_status[collection_name] = "Procesando..."
    print_progress_table()

    # Eliminar la colección si se seleccionó sobrescribir
    if collection_name in collections_to_overwrite:
        db[collection_name].drop()
    
    total_restored = 0

    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            for json_file in zipf.namelist():
                if json_file.endswith('.json'):
                    json_data = zipf.read(json_file)
                    documents = json.loads(json_data)
                    if documents:
                        db[collection_name].insert_many(documents)
                        total_restored += len(documents)

    # Comprobar que la colección se ha creado y que los datos coinciden
    restored_count = db[collection_name].count_documents({})
    if restored_count == total_restored:
        collection_status[collection_name] = f"Restaurada (OK)"
    else:
        collection_status[collection_name] = f"Error en restauración"
    
    print_progress_table()

# Mostrar la lista de colecciones
print("Listando todas las colecciones:")
print_progress_table()

# Restaurar las copias de seguridad de todas las colecciones seleccionadas
for collection_name in final_collections:
    restore_collection_from_zip(collection_name, backup_files[collection_name])

print(f"Restauraciones completadas desde la carpeta '{backup_dir}'")

input(Fore.YELLOW + "Pulsa [Enter] para volver al menú principal.")
os.system('python3 main.py')
