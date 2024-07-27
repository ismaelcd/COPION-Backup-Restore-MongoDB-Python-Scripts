# COPION Backup & Restore MongoDB Scripts

Este conjunto de scripts permite realizar copias de seguridad (backups) y restauraciones (restores) de bases de datos MongoDB de manera fácil y eficiente. También incluye una funcionalidad para configurar la conexión a MongoDB.

## Requisitos

Asegúrate de tener instaladas las siguientes dependencias antes de ejecutar los scripts:

```
pip install -r requirements.txt
```

## Archivos

- **main.py**: Script principal que permite seleccionar entre realizar un backup, restaurar un backup o configurar la conexión a MongoDB.
- **backup-mongodb.py**: Script para realizar backups de las colecciones de MongoDB.
- **restore-mongodb.py**: Script para restaurar backups de las colecciones de MongoDB.

## Configuración Inicial

Antes de ejecutar cualquier script, debes configurar la conexión a MongoDB. Si no se ha configurado el archivo `.env`, el script principal (**main.py**) te guiará a través del proceso de configuración.

## Uso

### Ejecutar el Script Principal

Para iniciar, ejecuta el script **main.py**:

```
python3 main.py
```
## Menú Principal

Una vez que ejecutes **main.py**, verás un menú con las siguientes opciones:

- **Realizar backup**: Esta opción ejecutará el script **backup-mongodb.py** para crear una copia de seguridad de las colecciones seleccionadas.
- **Restaurar backup**: Esta opción ejecutará el script **restore-mongodb.py** para restaurar las colecciones desde los backups disponibles.
- **Configurar conexión a MongoDB**: Esta opción te permitirá configurar la URL de conexión a MongoDB y el nombre de la base de datos.
- **Salir**: Saldrá del script.

## Realizar Backup

Selecciona "Realizar backup" en el menú principal para ejecutar **backup-mongodb.py**. Este script:

- Lista todas las colecciones disponibles en la base de datos.
- Te permite seleccionar las colecciones que deseas respaldar.
- Pregunta si deseas sobrescribir los backups existentes para las colecciones seleccionadas.
- Crea backups de las colecciones seleccionadas en la carpeta `backups-mongodb`.

Durante el proceso de backup, se mostrará una tabla con el progreso de cada colección.

## Restaurar Backup

Selecciona "Restaurar backup" en el menú principal para ejecutar **restore-mongodb.py**. Este script:

- Lista todas las colecciones disponibles en los backups.
- Te permite seleccionar las colecciones que deseas restaurar.
- Pregunta si deseas sobrescribir las colecciones existentes en la base de datos.
- Restaura las colecciones seleccionadas desde los backups en la carpeta `backups-mongodb`.

Durante el proceso de restauración, se mostrará una tabla con el progreso de cada colección.

## Archivos de Configuración

### `.env`

El archivo `.env` debe contener las siguientes variables de entorno:

- `MONGODB_URL`: La URL de conexión a MongoDB.
- `MONGODB_DB`: El nombre de la base de datos.

### `requirements.txt`

El archivo `requirements.txt` debe incluir las siguientes dependencias:

- `pymongo`
- `python-dotenv`
- `prettytable`
- `colorama`
- `inquirer`
- `inputimeout`

## Ejemplo de Archivo .env
```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=mi_base_de_datos
```
## Notas

- Asegúrate de que la carpeta `backups-mongodb` existe en el directorio de trabajo.
- Los backups se almacenan en subcarpetas dentro de `backups-mongodb`, una subcarpeta por cada colección.
- Cada colección respaldada se guarda en archivos ZIP divididos en partes de 2 GB si es necesario.
- Durante la restauración, el script busca los archivos ZIP correspondientes y restaura los datos en la base de datos.

¡Gracias por usar estos scripts! Si tienes alguna pregunta o problema, no dudes en contactarme.
