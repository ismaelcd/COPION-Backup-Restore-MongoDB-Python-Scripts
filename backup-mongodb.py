import os
import platform
import sys
import shutil
from pymongo import MongoClient
from dotenv import load_dotenv
import json
from datetime import datetime
import zipfile
from prettytable import PrettyTable
import time
import inquirer
from colorama import init, Fore, Style

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
    print(Fore.CYAN + "🄱🄰🄲🄺🅄🄿".center(110))
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

# Crear la carpeta de backups si no existe
backup_dir = "backups-mongodb"
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

# Obtener todas las colecciones de la base de datos y ordenarlas alfabéticamente
collections = sorted(db.list_collection_names())

# Preguntar al usuario qué colecciones desea respaldar
questions = [
    inquirer.Checkbox('collections',
                      message="Seleccione las colecciones que desea respaldar",
                      choices=collections)
]

answers = inquirer.prompt(questions)
selected_collections = answers['collections']

# Preguntar si se desea sobrescribir si ya existe un backup
overwrite_questions = []
for collection in selected_collections:
    backup_path = os.path.join(backup_dir, collection)
    if os.path.exists(backup_path):
        overwrite_questions.append(
            inquirer.Confirm(f'overwrite_{collection}',
                             message=f"El backup de la colección '{collection}' ya existe. ¿Desea sobrescribirlo?",
                             default=False)
        )

overwrite_answers = inquirer.prompt(overwrite_questions)

# Filtrar colecciones que no se desean sobrescribir y ordenarlas alfabéticamente
final_collections = []
collections_to_overwrite = []
for collection in selected_collections:
    backup_path = os.path.join(backup_dir, collection)
    if os.path.exists(backup_path):
        if overwrite_answers.get(f'overwrite_{collection}', True):
            collections_to_overwrite.append(collection)
        else:
            continue
    final_collections.append(collection)

final_collections.sort()

# Tamaño máximo de cada archivo ZIP en bytes (2 GB)
MAX_ZIP_SIZE = 2 * 1024 * 1024 * 1024

# Tamaño del lote de documentos a procesar en cada iteración
BATCH_SIZE = 1000

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
        elif "Copiada" in status:
            truncated_status = Fore.GREEN + truncated_status + Style.RESET_ALL
        else:
            truncated_status = Fore.WHITE + truncated_status + Style.RESET_ALL

        table.add_row([truncated_col, truncated_status])
    table._max_width = {"Colección": max_collection_name_length, "Estado": max_status_length}
    table.min_table_width = 110
    print(table)
    print("\n")

# Función para crear un archivo ZIP de un fragmento de documentos
def create_zip(backup_dir, collection_name, timestamp, part_number, documents):
    collection_backup_dir = f"{backup_dir}/{collection_name}"
    if not os.path.exists(collection_backup_dir):
        os.makedirs(collection_backup_dir)

    zip_file_path = f"{backup_dir}/{collection_name}/{collection_name}_{timestamp}_part{part_number}.zip"
    with zipfile.ZipFile(zip_file_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
        json_data = json.dumps(documents, default=str)
        zipf.writestr(f"{collection_name}_{timestamp}_part{part_number}.json", json_data)

    return os.path.getsize(zip_file_path)

# Función para eliminar backups antiguos de una colección
def delete_old_backups(collection_name):
    backup_path = os.path.join(backup_dir, collection_name)
    if os.path.exists(backup_path):
        shutil.rmtree(backup_path)

# Función para copiar una colección
def backup_collection(collection_name):
    if collection_name in collections_to_overwrite:
        delete_old_backups(collection_name)
    
    collection_status[collection_name] = "Procesando..."
    print_progress_table()
    
    collection = db[collection_name]
    total_documents = collection.count_documents({})
    copied_documents = 0

    # Crear una carpeta para la colección
    collection_backup_dir = f"{backup_dir}/{collection_name}"
    if not os.path.exists(collection_backup_dir):
        os.makedirs(collection_backup_dir)

    # Crear un nombre base para los archivos de la copia de seguridad
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    part_number = 1
    current_part_documents = []
    current_size = 0
    total_size = 0

    last_print_time = time.time()

    for doc in collection.find().batch_size(BATCH_SIZE):
        doc_size = len(json.dumps(doc, default=str).encode('utf-8'))
        if current_size + doc_size > MAX_ZIP_SIZE:
            part_size = create_zip(collection_backup_dir, collection_name, timestamp, part_number, current_part_documents)
            total_size += part_size
            part_number += 1
            current_part_documents = []
            current_size = 0

        current_part_documents.append(doc)
        current_size += doc_size
        copied_documents += 1

        # Calcular y mostrar el progreso
        percentage = (copied_documents / total_documents) * 100

        if time.time() - last_print_time >= 5:
            collection_status[collection_name] = f"Procesando... {percentage:.2f}%"
            print_progress_table()
            last_print_time = time.time()

    if current_part_documents:
        part_size = create_zip(collection_backup_dir, collection_name, timestamp, part_number, current_part_documents)
        total_size += part_size

    total_size_mb = total_size / (1024 * 1024)
    if total_size_mb >= 1024:
        total_size_str = f"{total_size_mb / 1024:.2f} GB"
    else:
        total_size_str = f"{total_size_mb:.2f} MB"

    collection_status[collection_name] = f"Copiada (OK) {total_size_str}"
    print_progress_table()

# Mostrar la lista de colecciones
print("Listando todas las colecciones:")
print_progress_table()

# Crear copias de seguridad de todas las colecciones seleccionadas
for collection_name in final_collections:
    backup_collection(collection_name)

print(f"Backups completados en la carpeta '{backup_dir}'")

input(Fore.YELLOW + "Pulsa [Enter] para volver al menú principal.")
os.system('python3 main.py')
