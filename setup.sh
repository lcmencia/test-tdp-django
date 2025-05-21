#!/bin/bash

# Script de configuración inicial

echo "Verificando y configurando el archivo .env..."
if [ ! -f .env ]; then
    echo ".env no encontrado. Copiando .env.example a .env"
    cp .env.example .env
    echo ".env creado. Por favor, edita el archivo .env con tus configuraciones."
else
    echo ".env ya existe."
fi

# Verificar si SECRET_KEY existe en .env y generarla si no
if ! grep -q "^SECRET_KEY=" .env; then
    echo "SECRET_KEY no encontrada en .env. Generando una nueva..."
    # Generar una SECRET_KEY usando Python
    SECRET_KEY=$(python -c '
import random
import string
chars = string.ascii_letters + string.digits + string.punctuation
secret_key = "".join(random.choice(chars) for i in range(50))
print(secret_key)
')
    echo "SECRET_KEY=$SECRET_KEY" >> .env
    echo "SECRET_KEY añadida a .env"
else
    echo "SECRET_KEY ya existe en .env."
fi

echo ""
echo "Construyendo la imagen de Docker..."
docker build -f Dockerfile -t pizzeria_django .

if [ $? -eq 0 ]; then
    echo "Imagen de Docker construida exitosamente."
    echo ""
    echo "Levantando los servicios con Docker Compose..."
    docker-compose up -d --build
    if [ $? -eq 0 ]; then
        echo "Servicios de Docker Compose iniciados en segundo plano."
        echo "Puedes ver los logs con: docker-compose logs -f"
        echo "Para detener los servicios: docker-compose down"
        echo ""
        echo "Ejecutando tests..."
        docker-compose exec web pytest
        if [ $? -eq 0 ]; then
            echo "Tests ejecutados exitosamente."
        else
            echo "Error al ejecutar los tests."
            # No salir aquí para permitir que los servicios sigan corriendo si los tests fallan
        fi
    else
        echo "Error al iniciar los servicios de Docker Compose."
        exit 1
    fi
else
    echo "Error al construir la imagen de Docker."
    exit 1
fi

echo ""
echo "Configuración inicial completada."
echo "Recuerda revisar y editar el resto de las configuraciones en el archivo .env."
