# 🧬 Biobanco

Bienvenido al repositorio de **Biobanco**, una aplicación **Django** diseñada para facilitar la gestión y almacenamiento de información para biobancos.

## 📋 Requisitos previos

Asegúrate de tener instalado:

- Python 3.8 o superior 🐍
- Django 3.2 o superior 🕸

## 🛠 Configuración del entorno de desarrollo

Recomendamos utilizar un entorno virtual para instalar las dependencias del proyecto. Sigue estos pasos para crearlo y activarlo:


python3 -m venv venv
source venv/bin/activate  # En Windows use: .\venv\Scripts\activate


Con el entorno virtual activado, instala las dependencias con:


pip install -r requirements.txt


## 🚀 Configuración del proyecto

1. Renombra el archivo `.env.example` a `.env` y configura las variables de entorno según sea necesario.
2. Realiza las migraciones necesarias con:


python manage.py migrate


3. Crea un superusuario para acceder al panel de administración con:


python manage.py createsuperuser


## ⚙️ Poner en marcha el proyecto

Para iniciar el servidor de desarrollo, usa:


python manage.py runserver


Ahora, abre tu navegador y visita [http://127.0.0.1:8000/](http://127.0.0.1:8000/) para ver la aplicación en funcionamiento.

## 🧪 Tests

Para ejecutar las pruebas del proyecto, use:


python manage.py test



## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo [LICENSE.md](LICENSE.md) para más detalles.
