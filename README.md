# 🧬 Biobanco

Bienvenido al repositorio de **Biobanco**, una aplicación innovadora desarrollada con **Django** que se especializa en la gestión y almacenamiento eficiente de muestras para biobancos. Esta herramienta proporciona una plataforma robusta para rastrear muestras y envíos con un enfoque en la trazabilidad y la seguridad de los datos.

## 📋 Requisitos previos

Antes de comenzar, asegúrate de tener:

- **Python 3.8** o superior 🐍
- **Django 3.2** o superior 🕸

## 🛠 Configuración del entorno de desarrollo

Para una gestión eficiente de las dependencias, recomendamos usar un entorno virtual:

```bash
python3 -m venv venv
# En Windows use: .\venv\Scripts\activate
# En MacOS/Linux use: source venv/bin/activate
```

## 🚀 Configuración del proyecto

Sigue estos pasos para configurar tu proyecto:

1. **Configuración del entorno**:
   - Renombra `.env.example` a `.env`.
   - Ajusta las variables de entorno según tus necesidades.

2. **Migraciones de la base de datos**:
   ```bash
   python3 manage.py makemigrations
   python3 manage.py makemigrations accounts
   python3 manage.py migrate
   ```

3. **Creación del superusuario y roles**:
   - Accede a la terminal de Python:
     ```bash
     python manage.py shell
     ```
   - Importa y crea roles:
     ```python
     from accounts.models import Role
     Role.objects.create(id_role=Role.ADMIN)
     Role.objects.create(id_role=Role.SUPERVISOR)
     Role.objects.create(id_role=Role.TECNICO)
     ```
   - Finalmente, crea el superusuario:
     ```bash
     python3 manage.py createsuperuser
     ```

## 🧱 Gestión de Espacios de Almacenamiento

Después de crear el superusuario, sigue estos pasos para configurar los espacios de almacenamiento:

1. Accede al panel de administración de Django.
2. Crea los espacios de almacenamiento necesarios:
   - **Freezers**
   - **Racks**
   - **Cajas**

   Asegúrate de que estos espacios estén correctamente registrados y existan en el sistema antes de proceder.

3. Una vez configurados, puedes comenzar a crear **muestras** y **envíos**. La aplicación proporciona una trazabilidad completa de muestras, envíos y acciones realizadas.

## ⚙️ Iniciar el proyecto

Para lanzar el servidor de desarrollo:

```bash
python3 manage.py runserver
```

Visita [http://127.0.0.1:8000/](http://127.0.0.1:8000/) en tu navegador para acceder a la aplicación.

## 🧪 Tests

Ejecuta las pruebas con:

```bash
python3 manage.py test
```

## 🔐 Roles y permisos

El sistema cuenta con tres roles fundamentales:

- **ADMIN**: Gestión total del sistema.
- **SUPERVISOR**: Supervisa las operaciones y maneja datos críticos.
- **TECNICO**: Encargado de la gestión de muestras y registros.

## Aqui hay algunas vistas del proyecto:

Visita [https://drive.google.com/drive/folders/1Rb8b4v2axPJcGL_PRtiF7h9B1uG5ATlI?usp=sharing]


para ver las vistas! 

Espero les guste! :D 

## 📜 Licencia

Este proyecto está bajo la Licencia MIT.




