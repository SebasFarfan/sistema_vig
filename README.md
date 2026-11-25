<h1>Proyecto Sistema de Vigilantes</h1>

- Crear entorno virtual 

`python -m venv .venv`

Activar el entorno virtual


|Sistema operativo / Terminal|	Comando de activación                     |
|----------------------------|--------------------------------------------|
|Windows (CMD)               |  	.venv\Scripts\activate.bat              |
|Windows (PowerShell)        |   	.venv\Scripts\Activate.ps1              |
|Windows (Git Bash)          |   	source .venv/Scripts/activate           |
|macOS / Linux	             |    source .venv/bin/activate               |


Luego instalar las librerias en base a al archivo requirements.txt

`pip install -r requirements.txt`

- Crear su base de datos mysql en su Computadora, usando workbench.

- Una vez creada la base de datos agregarla en su configuración del archivo ***config.yaml***.


- Crear un archivo llamado ***config.yaml*** con el siguiente contendido:
  
  db:
  
  usuario: [nombre de usuario de base de datos]
  
  password: [password]
  
  host: "localhost"
  
  puerto: 3306
  
  nombre: [nombre de la base de datos]

  ---
-  Después de definir la base de datos:

  se ejecuta el archivo main.py que tiene el pipeline del ETL

  ---

- Antes de iniciar la aplicación:

  Recordar que Se debe crear la base de datos en Mysql.

  Luego ejecutar el archivo 'crear_usuario.py' que se encuentra en la carpeta 'app', ingresar un nombre de usuario y password.

  Una vez creado un usario administrador en la base de datos.

  Ejecutar el archivo 'app.py' que está en la carpeta 'app' con el comando 'streamlit run app.py'.

  Ingresar las credenciales de administrador para ingresar al sistema.


