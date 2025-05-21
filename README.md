# Nombre del Proyecto

Una descripción concisa de tu proyecto Django.

## Tabla de Contenidos

- [Getting Started](#getting-started)
  - [Prerrequisitos](#prerrequisitos)
  - [Clonar el Repositorio](#clonar-el-repositorio)
  - [Opciones de Configuración](#opciones-de-configuración)
    - [Opción 1: Usar Scripts de Configuración Automática](#opción-1-usar-scripts-de-configuración-automática)
    - [Opción 2: Configuración Manual Paso a Paso](#opción-2-configuración-manual-paso-a-paso)
- [Tests](#tests)
  - [Ejecutar Tests](#ejecutar-tests)
- [Comandos Útiles de Docker Compose](#comandos-útiles-de-docker-compose)
- [Documentación de la API](#documentación-de-la-api)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Licencia](#licencia)

## Getting Started

Estas instrucciones te guiarán para obtener una copia del proyecto en funcionamiento en tu máquina local para propósitos de desarrollo y pruebas.

### Prerrequisitos

Necesitas tener instalado lo siguiente:

*   Python 3.x
*   pip (administrador de paquetes de Python)
*   Docker y Docker Compose (si planeas usar Docker)

### Clonar el Repositorio

Clona el repositorio a tu máquina local:

```bash
git clone https://github.com/lcmencia/test-tdp-django.git
cd test-tdp-django
```

### Opciones de Configuración

Tienes dos opciones para configurar el proyecto: usando los scripts de configuración automática o realizando los pasos manualmente.

#### Opción 1: Usar Scripts de Configuración Automática

Para automatizar los pasos iniciales de configuración (copiar `.env.example`, generar `SECRET_KEY` si no existe, construir la imagen de Docker, levantar los servicios con Docker Compose y ejecutar los tests), puedes usar el script de configuración apropiado para tu sistema operativo:

**Para Linux/macOS (Bash):**

```bash
chmod +x setup.sh
./setup.sh
```

**Para Windows (PowerShell):**

Abre PowerShell en el directorio raíz del proyecto y ejecuta:

```powershell
.\setup.ps1
```

Puede que necesites ajustar la política de ejecución de scripts en PowerShell si no puedes ejecutar scripts locales. Consulta la documentación de PowerShell para más detalles.

#### Opción 2: Configuración Manual Paso a Paso

Si prefieres configurar el proyecto manualmente, sigue estos pasos:

1.  **Configurar el Entorno:**
    Crea un archivo `.env` en el directorio raíz del proyecto copiando el archivo de ejemplo:
    ```bash
    cp .env.example .env
    ```
    *(Para Windows, usa `Copy-Item .env.example .env` en PowerShell o `copy .env.example .env` en CMD)*.
    Edita el archivo `.env` y configura las variables de entorno necesarias, como `DATABASE_URL`, etc.

2.  **Generar SECRET_KEY (si no existe):**
    Si el archivo `.env` no contiene una línea que comience con `SECRET_KEY=`, puedes generar una usando Python y añadirla al archivo. Ejecuta el siguiente comando en la raíz del proyecto:
    ```bash
    python -c '
import random
import string
chars = string.ascii_letters + string.digits + string.punctuation
secret_key = "".join(random.choice(chars) for i in range(50))
print(f"SECRET_KEY={secret_key}")
' >> .env
    ```
    *(Este comando funciona tanto en Bash como en PowerShell si Python está en el PATH)*.

3.  **Construir la Imagen de Docker:**
    Construye la imagen de Docker para la aplicación web:
    ```bash
    docker build -f Dockerfile -t pizzeria_django .
    ```

4.  **Levantar los Servicios con Docker Compose:**
    Usa Docker Compose para iniciar los servicios de base de datos y web definidos en `docker-compose.yml`. La opción `--build` asegura que la imagen se construya si es necesario, y `-d` ejecuta los contenedores en segundo plano.
    ```bash
    docker-compose up -d --build
    ```

5.  **Ejecutar Migraciones de Base de Datos:**
    Una vez que los servicios estén corriendo y la base de datos esté saludable, aplica las migraciones de Django dentro del contenedor web:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

6.  **Crear Usuarios (Opcional):**
    Puedes crear un superusuario, usuario staff y/o usuario normal utilizando el script `create_superuser.py` dentro del contenedor web. Asegúrate de configurar las variables de entorno `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD`, `DJANGO_STAFF_USERNAME`, `DJANGO_STAFF_PASSWORD`, `DJANGO_NORMAL_USERNAME`, `DJANGO_NORMAL_PASSWORD` en tu archivo `.env` antes de ejecutar este paso si quieres crear usuarios staff o normales.
    ```bash
    docker-compose exec web python create_superuser.py
    ```

7.  **Ejecutar Tests:**
    Para verificar que todo funciona correctamente, ejecuta los tests dentro del contenedor web:
    ```bash
    docker-compose exec web pytest
    ```

8.  **Ejecutar el Servidor de Desarrollo (Manual, si no usas Docker Compose para esto):**
    Si no usaste `docker-compose up` para mantener el servidor web corriendo en segundo plano, puedes iniciarlo manualmente dentro del contenedor web para desarrollo:
    ```bash
    docker-compose exec web python manage.py runserver 0.0.0.0:8000
    ```
    El servidor estará disponible en `http://127.0.0.1:8000/`.

## Tests

### Ejecutar Tests

Para ejecutar los tests del proyecto manualmente (fuera del script de configuración), usa pytest dentro del contenedor web:

```bash
docker-compose exec web pytest
```

### Comandos Útiles de Docker Compose

*   Detener los servicios:
    ```bash
    docker-compose down
    ```
*   Ejecutar comandos dentro del contenedor de la aplicación (por ejemplo, shell de Django):
    ```bash
    docker-compose exec web python manage.py shell
    ```
    Reemplaza `web` con el nombre del servicio de tu aplicación en `docker-compose.yml`.
*   Ver logs de los servicios:
    ```bash
    docker-compose logs -f
    ```

## Documentación de la API

La API de la Pizzería proporciona endpoints para la gestión de usuarios, autenticación y pedidos. La documentación interactiva de la API está disponible a través de Swagger UI y ReDoc.

### Visualizar la Documentación

Una vez que el servidor esté corriendo (ver sección [Getting Started](#getting-started)), puedes acceder a la documentación en los siguientes enlaces:

*   **Swagger UI:** `http://127.0.0.1:8000/swagger/`
*   **ReDoc:** `http://127.0.0.1:8000/redoc/`

### Endpoints de Autenticación

La API soporta autenticación basada en Token de Django REST Framework y autenticación basada en JWT.

#### Autenticación con Token (DRF)

*   **Obtener Token:** `POST /api-token-auth/`
    *   **Descripción:** Obtiene un token de autenticación para un usuario.
    *   **Request Body:** `{"username": "your_username", "password": "your_password"}`
    *   **Ejemplo con curl:**
        ```bash
        curl -X POST http://127.0.0.1:8000/api-token-auth/ \
        -H "Content-Type: application/json" \
        -d '{"username": "your_username", "password": "your_password"}'
        ```

#### Autenticación con JWT (Simple JWT)

*   **Obtener Tokens (Access y Refresh):** `POST /auth/token/`
    *   **Descripción:** Obtiene un par de tokens (acceso y refresco) para un usuario.
    *   **Request Body:** `{"username": "your_username", "password": "your_password"}`
    *   **Ejemplo con curl:**
        ```bash
        curl -X POST http://127.0.0.1:8000/auth/token/ \
        -H "Content-Type: application/json" \
        -d '{"username": "your_username", "password": "your_password"}'
        ```

*   **Refrescar Token de Acceso:** `POST /auth/token/refresh/`
    *   **Descripción:** Obtiene un nuevo token de acceso utilizando un token de refresco válido.
    *   **Request Body:** `{"refresh": "your_refresh_token"}`
    *   **Ejemplo con curl:**
        ```bash
        curl -X POST http://127.0.0.1:8000/auth/token/refresh/ \
        -H "Content-Type: application/json" \
        -d '{"refresh": "your_refresh_token"}'
        ```

*   **Verificar Token de Acceso:** `POST /auth/token/verify/`
    *   **Descripción:** Verifica la validez de un token de acceso.
    *   **Request Body:** `{"token": "your_access_token"}`
    *   **Ejemplo con curl:**
        ```bash
        curl -X POST http://127.0.0.1:8000/auth/token/verify/ \
        -H "Content-Type: application/json" \
        -d '{"token": "your_access_token"}'
        ```

### Endpoints de Pizzería

Estos endpoints permiten gestionar pizzas e ingredientes. La mayoría requieren autenticación.

*   **Listar Pizzas / Crear Pizza:** `GET /api/pizzas/`, `POST /api/pizzas/`
    *   **Descripción:** Obtiene la lista de todas las pizzas o crea una nueva pizza.
    *   **Ejemplo GET con curl (requiere autenticación):**
        ```bash
        curl -X GET http://127.0.0.1:8000/api/pizzas/ \
        -H "Authorization: Token your_auth_token"
        # O con JWT:
        # -H "Authorization: Bearer your_access_token"
        ```
    *   **Ejemplo POST con curl (requiere autenticación):**
        ```bash
        curl -X POST http://127.0.0.1:8000/api/pizzas/ \
        -H "Content-Type: application/json" \
        -H "Authorization: Token your_auth_token" \
        -d '{"name": "Pizza de Prueba", "description": "Una pizza deliciosa", "price": 12.50}'
        # O con JWT:
        # -H "Authorization: Bearer your_access_token"
        ```

*   **Ver Detalle de Pizza:** `GET /api/pizzas/<int:pk>/`
    *   **Descripción:** Obtiene los detalles de una pizza específica por su ID.
    *   **Ejemplo con curl (requiere autenticación):**
        ```bash
        curl -X GET http://127.0.0.1:8000/api/pizzas/1/ \
        -H "Authorization: Token your_auth_token"
        # O con JWT:
        # -H "Authorization: Bearer your_access_token"
        ```

*   **Actualizar Pizza:** `PUT /api/pizzas/<int:pk>/update/`, `PATCH /api/pizzas/<int:pk>/update/`
    *   **Descripción:** Actualiza completamente (PUT) o parcialmente (PATCH) una pizza por su ID.
    *   **Ejemplo PATCH con curl (requiere autenticación):**
        ```bash
        curl -X PATCH http://127.0.0.1:8000/api/pizzas/1/update/ \
        -H "Content-Type: application/json" \
        -H "Authorization: Token your_auth_token" \
        -d '{"price": 15.00}'
        # O con JWT:
        # -H "Authorization: Bearer your_access_token"
        ```

*   **Añadir Ingrediente a Pizza:** `POST /api/pizzas/<int:pk>/add_ingredient/<int:ingredient_pk>/`
    *   **Descripción:** Añade un ingrediente a una pizza específica.
    *   **Ejemplo con curl (requiere autenticación):**
        ```bash
        curl -X POST http://127.0.0.1:8000/api/pizzas/1/add_ingredient/5/ \
        -H "Authorization: Token your_auth_token"
        # O con JWT:
        # -H "Authorization: Bearer your_access_token"
        ```

*   **Eliminar Ingrediente de Pizza:** `POST /api/pizzas/<int:pk>/remove_ingredient/<int:ingredient_pk>/`
    *   **Descripción:** Elimina un ingrediente de una pizza específica.
    *   **Ejemplo con curl (requiere autenticación):**
        ```bash
        curl -X POST http://127.0.0.1:8000/api/pizzas/1/remove_ingredient/5/ \
        -H "Authorization: Token your_auth_token"
        # O con JWT:
        # -H "Authorization: Bearer your_access_token"
        ```

*   **Listar Ingredientes / Crear Ingrediente:** `GET /api/ingredients/`, `POST /api/ingredients/`
    *   **Descripción:** Obtiene la lista de todos los ingredientes o crea un nuevo ingrediente.
    *   **Ejemplo GET con curl (requiere autenticación):**
        ```bash
        curl -X GET http://127.0.0.1:8000/api/ingredients/ \
        -H "Authorization: Token your_auth_token"
        # O con JWT:
        # -H "Authorization: Bearer your_access_token"
        ```
    *   **Ejemplo POST con curl (requiere autenticación):**
        ```bash
        curl -X POST http://127.0.0.1:8000/api/ingredients/ \
        -H "Content-Type: application/json" \
        -H "Authorization: Token your_auth_token" \
        -d '{"name": "Tomate"}'
        # O con JWT:
        # -H "Authorization: Bearer your_access_token"
        ```

*   **Ver Detalle / Actualizar / Eliminar Ingrediente:** `GET /api/ingredients/<int:pk>/`, `PUT /api/ingredients/<int:pk>/`, `PATCH /api/ingredients/<int:pk>/`, `DELETE /api/ingredients/<int:pk>/`
    *   **Descripción:** Obtiene, actualiza o elimina un ingrediente específico por su ID.
    *   **Ejemplo DELETE con curl (requiere autenticación):**
        ```bash
        curl -X DELETE http://127.0.0.1:8000/api/ingredients/1/ \
        -H "Authorization: Token your_auth_token"
        # O con JWT:
        # -H "Authorization: Bearer your_access_token"
        ```

## Estructura del Proyecto

(Opcional: Describe brevemente la estructura de directorios principal de tu proyecto)

```
.
├── authentication/
├── myproject/
├── pizzeria/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── README.md
├── requirements.txt
└── ...otros archivos
```

## Licencia

Este proyecto está bajo la Licencia [Nombre de la Licencia] - mira el archivo [LICENSE](LICENSE) para detalles.
