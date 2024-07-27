import os
import platform
import sys
import time
import inquirer
from colorama import init, Fore, Style
from dotenv import load_dotenv

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
    print(Fore.CYAN + "🄱🄰🄲🄺🅄🄿 & 🅁🄴🅂🅃🄾🅁🄴".center(110))
    print(Fore.CYAN + " ")
    print(Fore.CYAN + "By Ismael Cruz".center(110))
    print(Fore.CYAN + "=" * 110)
    print(Fore.CYAN + " ")

def configure_env():
    print(" ")
    print(" ")
    print(Fore.YELLOW + "Configuración de la conexión a MongoDB".center(110))
    print(" ")
    mongo_url = input(Fore.CYAN + "   Ingrese la URL de conexión a MongoDB: ")
    db_name = input(Fore.CYAN + "   Ingrese el nombre de la base de datos: ")

    with open('.env', 'w') as env_file:
        env_file.write(f"MONGODB_URL={mongo_url}\n")
        env_file.write(f"MONGODB_DB={db_name}\n")

    print(Fore.GREEN + "Configuración guardada exitosamente.".center(110))
    print(Fore.GREEN + "Reiniciando el script...".center(110))
    time.sleep(2)
    os.execv(sys.executable, ['python3'] + sys.argv)

def load_config():
    if not os.path.exists('.env'):
        print(Fore.RED + "Archivo de configuración .env no encontrado. Por favor, configure primero.".center(110))
        return False

    load_dotenv()

    if not os.getenv("MONGODB_URL") or not os.getenv("MONGODB_DB"):
        print(Fore.RED + "Variables de entorno incompletas. Por favor, configure correctamente.".center(110))
        return False

    return True

def main():
    clear_console()
    print_header()

    if not load_config():
        configure_env()
        return

    questions = [
        inquirer.List('action',
                      message="Seleccione una opción",
                      choices=['Realizar backup', 'Restaurar backup', 'Configurar conexión a MongoDB', 'Salir'])
    ]

    answer = inquirer.prompt(questions)['action']
    print(Fore.CYAN + "=" * 110 + "\n")

    if answer == 'Realizar backup':
        os.system('python3 backup-mongodb.py')
    elif answer == 'Restaurar backup':
        os.system('python3 restore-mongodb.py')
    elif answer == 'Configurar conexión a MongoDB':
        configure_env()
    elif answer == 'Salir':
        print(Fore.GREEN + "Gracias por usar el script. ¡Adiós!".center(110))
        sys.exit()

if __name__ == '__main__':
    main()
