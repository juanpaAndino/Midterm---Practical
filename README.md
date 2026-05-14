# API de Autenticación Segura - Proyecto de Ciberseguridad

Este repositorio contiene el código fuente para el proyecto final de la materia de Ciberseguridad. Es una API construida con FastAPI y SQLModel que implementa un sistema de gestión de identidades enfocado en el almacenamiento seguro de credenciales.

A diferencia de implementaciones básicas, este proyecto no guarda contraseñas en texto plano ni usa algoritmos rápidos como MD5 o SHA-256. Toda la seguridad se maneja con Bcrypt puro, integrando técnicas de Salting dinámico y Peppering a través de variables de entorno para mitigar ataques de fuerza bruta y tablas precomputadas.

## Requisitos previos

Para correr este proyecto necesitas tener instalado Python en tu sistema. Se recomienda levantar un entorno virtual (venv) antes de instalar las dependencias.

Las librerías requeridas son:
- fastapi[all]
- sqlmodel
- bcrypt
- python-dotenv

## Instalación y configuración

1. Abre una terminal en la carpeta raíz del proyecto.
2. Instala las dependencias ejecutando el siguiente comando:

   pip install "fastapi[all]" sqlmodel bcrypt python-dotenv

3. Configuración del Pepper: Este paso es estrictamente obligatorio por diseño de seguridad. La aplicación arrojará un RuntimeError y no arrancará si no detecta el secreto global.
   Crea un archivo llamado exactamente `.env` en la misma carpeta donde está el main.py y agrega la siguiente línea:

   APP_PEPPER="S3cr3t_P3pp3r_UIDE_2026!"

   Nota de seguridad: El archivo .env nunca debe ser subido al control de versiones.

## Ejecución

Una vez instaladas las dependencias y configurado el entorno, levanta el servidor local ejecutando:

uvicorn main:app --reload

La base de datos SQLite (database.db) se construirá automáticamente al iniciar la aplicación por primera vez.

## Uso y Pruebas

FastAPI genera una interfaz gráfica interactiva por defecto. Para probar el sistema sin necesidad de Postman, abre tu navegador y dirígete a:

http://127.0.0.1:8000/docs

Rutas disponibles:
- POST /register : Recibe username y password en texto plano. El sistema concatena el Pepper, genera un Salt aleatorio mediante Bcrypt, procesa el hash con un factor de costo de 12 y almacena el registro.
- POST /login : Recibe credenciales. Aplica el Pepper estático a la contraseña recibida y la compara mediante validación de bytes contra el hash almacenado en SQLite.