# 🧬 Biobanco

Bienvenido al repositorio de **Biobanco**, una aplicación **Django** diseñada para facilitar la gestión y almacenamiento de información para biobancos.

## 📋 Requisitos previos

Asegúrate de tener instalado:

- Python 3.8 o superior 🐍
- Django 3.2 o superior 🕸

## 🛠 Configuración del entorno de desarrollo

Recomendamos utilizar un entorno virtual para instalar las dependencias del proyecto. Sigue estos pasos para crearlo y activarlo:

`python3 -m venv venv`

`source venv/bin/activate`  # En Windows use: `.\venv\Scripts\activate`


## 🚀 Configuración del proyecto

1. Renombra el archivo `.env.example` a `.env` y configura las variables de entorno según sea necesario.
2. Realiza las migraciones necesarias con:

- `python3 manage.py makemigrations`

- `python3 manage.py makemigrations acccounts`

- `python3 manage.py migrate`


3. Crea un superusuario para acceder al panel de administración con:

    1. - abrir terminal de python para crear roles con: 
    - `python manage.py shell`

    2. - Luego importar tabla de roles para crearlos : 
    - `from accounts.models import Role`
    - `Role.objects.create(id_role=Role.ADMIN)`
    - `Role.objects.create(id_role=Role.SUPERVISOR)`
    - `Role.objects.create(id_role=Role.TECNICO)`

    3. - Una vez creados se puede finalmente crear el superusuario:
    - `python3 manage.py createsuperuser`


## ⚙️ Poner en marcha el proyecto

Para iniciar el servidor de desarrollo, usa:


`python3 manage.py runserver`


Ahora, abre tu navegador y visita [http://127.0.0.1:8000/](http://127.0.0.1:8000/) para ver la aplicación en funcionamiento.

## 🧪 Tests

Para ejecutar las pruebas del proyecto, use:


`python3 manage.py test`



## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT 
