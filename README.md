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

## 📜 Licencia

Este proyecto está bajo la Licencia MIT.


aqui hay algunas vistas del proyecto:


![trazabilidad de muetras](https://github.com/sanjaygrr/Biobanco/assets/65647041/3e4da69b-9bb9-4551-b9fd-cdddfbaf8d2d)
![reporteria de muestras](https://github.com/sanjaygrr/Biobanco/assets/65647041/7c05c193-bbcb-4ebc-81a4-c665926c8085)
![reporteria de envios](https://github.com/sanjaygrr/Biobanco/assets/65647041/850fc9d4-9bc5-4ec5-bf01-87dce581b741)
![registro de ususario](https://github.com/sanjaygrr/Biobanco/assets/65647041/87c112ac-15c4-49a7-bcc4-38c2890f02dd)
![registrar espacio](https://github.com/sanjaygrr/Biobanco/assets/65647041/68edc99b-5f4c-4a4e-a4c6-4a5be4cd85a6)
![pop up eliminar muestra](https://github.com/sanjaygrr/Biobanco/assets/65647041/19f92b1d-521d-44dd-8d26-78d3b5ce5b24)
![nuevo envio](https://github.com/sanjaygrr/Biobanco/assets/65647041/fbc92a46-779b-47f8-84c4-97a42cfb321c)
![no se puede cambiar espacio](https://github.com/sanjaygrr/Biobanco/assets/65647041/7cee4940-a71e-4b13-8482-d202ec5eef6a)
![login](https://github.com/sanjaygrr/Biobanco/assets/65647041/52552528-ced1-4bfc-ae5a-b8bb4585de50)
![lista de ususarios](https://github.com/sanjaygrr/Biobanco/assets/65647041/9f37820c-047f-4be2-82a6-fb6c2463b24b)
![lista de espacios](https://github.com/sanjaygrr/Biobanco/assets/65647041/3aa8f3e5-693a-464b-b207-e6b31bf33551)
![home](https://github.com/sanjaygrr/Biobanco/assets/65647041/a3fd3697-a2b5-40b0-a70b-c34cc094c196)
![eliminar usuario](https://github.com/sanjaygrr/Biobanco/assets/65647041/e98ffc85-681e-4fb2-a7bb-7df23ab7ceff)
![editar_ver muestras](https://github.com/sanjaygrr/Biobanco/assets/65647041/33a4550c-1162-4117-8468-40aaa1c32535)
![editar usuarios](https://github.com/sanjaygrr/Biobanco/assets/65647041/fe9c1933-966f-4353-b232-24b9113cf220)
![editar muestra](https://github.com/sanjaygrr/Biobanco/assets/65647041/d3a5a0df-53f0-45b5-ab7a-4289bb2f5f92)
![crear muestra](https://github.com/sanjaygrr/Biobanco/assets/65647041/4b875199-cdf5-4ddc-a018-1c0ffbe82cf2)
![completa todos los cambios](https://github.com/sanjaygrr/Biobanco/assets/65647041/5d3cb8fe-a26f-40b5-8e6a-5e573ef32201)
![agregar muestras a envio](https://github.com/sanjaygrr/Biobanco/assets/65647041/8a582273-086f-492e-8c80-535b9f3dca40)


