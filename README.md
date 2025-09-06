# financial2
#  Financial API

API desarrollada con FastAPI y Streamlit para la gestión y consulta de información financiera de una empresa.  
La aplicación se conecta a una base de datos (MySQL) que contiene las tablas principales del sistema y permite realizar consultas comunes (**GET** y **POST**) utilizando sobretodo `JOIN` de todo tipo.

## Estructura del Proyecto

```
financial2/
│── .env                  # Variables de entorno (datos sensibles de conexión)
│── .gitignore            # Exclusión de archivos sensibles y virtualenv
│── db_schema.sql         # Esquema lógico de la base de datos (DDL)
│── requirements.txt      # Dependencias del proyecto
│── conexion.py           # Conexión a la base de datos MySQL
│── main.py               # Creación de la API con FastAPI + definición de tags
│── models.py             # Definición de Pydantic BaseModels (para cada tabla)
│── routers/              # Rutas organizadas de la API (endpoints GET y POST)
|── .env.example          #ejemplo de como configurar las variables de entorno
```

## Base de Datos

La API trabaja sobre un esquema financiero en MySQL con las siguientes tablas:

- accounts → Información de cuentas.

- clients → Datos de clientes.

- employees → Datos de empleados.

- loans → Préstamos otorgados.

- transfers → Transferencias realizadas.

- withdrawals → Retiros de dinero.

**El archivo db_schema.sql contiene la definición del esquema.

# Instalación y Configuración

1. Clonar el repositorio:
```
git clone https://github.com/vanesita1524/financial2.git
cd financial2
```
2. Crear y activar entorno virtual
```
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```
3. Instalar dependencias
```
pip install -r requirements.txt
```
4. Configurar variables de entorno en el archivo .env (no incluido en el repo por seguridad)
```
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_NAME=financial_db

## Ejecución del Proyecto
```
Levantar la API con FastAPI
```
uvicorn main:app --reload
```
La documentación interactiva estará disponible en:

Swagger UI → http://127.0.0.1:8000/docs

ReDoc → http://127.0.0.1:8000/redoc

Ejecutar la interfaz con Streamlit
```
streamlit run app.py
```
## Funcionamiento

Conexión a la base de datos

El archivo conexion.py maneja la conexión a MySQL utilizando las variables del .env. Se asegura de no exponer credenciales sensibles gracias a .gitignore.

Modelos de datos

En models.py se definen las clases BaseModel de Pydantic para validar la información de cada tabla.

Rutas y Endpoints

Las rutas están organizadas en la carpeta routers/. Se incluyen operaciones GET (consultas, joins entre tablas) y POST (creación de registros).

Los endpoints están documentados con tags en main.py para facilitar su uso en Swagger.


## Tecnologías Utilizadas
```
Python 3.10+

FastAPI (framework backend)

Streamlit (interfaz visual)

MySQL (base de datos relacional)

Pydantic (validación de datos)

Uvicorn (servidor ASGI)

dotenv (manejo de variables de entorno)
```
