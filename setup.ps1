# Script de configuración inicial para Windows (PowerShell)

Write-Host "Verificando y configurando el archivo .env..."
if (-not (Test-Path .env)) {
    Write-Host ".env no encontrado. Copiando .env.example a .env"
    Copy-Item .env.example .env
    Write-Host ".env creado. Por favor, edita el archivo .env con tus configuraciones."
} else {
    Write-Host ".env ya existe."
}

# Verificar si SECRET_KEY existe en .env y generarla si no
$envContent = Get-Content .env | Out-String
if ($envContent -notmatch "^SECRET_KEY=") {
    Write-Host "SECRET_KEY no encontrada en .env. Generando una nueva..."
    # Generar una SECRET_KEY usando Python
    $secretKey = python -c '
import random
import string
chars = string.ascii_letters + string.digits + string.punctuation
secret_key = "".join(random.choice(chars) for i in range(50))
print(secret_key)
'
    Add-Content .env "`nSECRET_KEY=$secretKey"
    Write-Host "SECRET_KEY añadida a .env"
} else {
    Write-Host "SECRET_KEY ya existe en .env."
}

Write-Host ""
Write-Host "Construyendo la imagen de Docker..."
docker build -f Dockerfile -t pizzeria_django .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Imagen de Docker construida exitosamente."
    Write-Host ""
    Write-Host "Levantando los servicios con Docker Compose..."
    docker-compose up -d --build
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Servicios de Docker Compose iniciados en segundo plano."
        Write-Host "Puedes ver los logs con: docker-compose logs -f"
        Write-Host "Para detener los servicios: docker-compose down"
        Write-Host ""
        Write-Host "Ejecutando tests..."
        docker-compose exec web pytest
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Tests ejecutados exitosamente."
        } else {
            Write-Host "Error al ejecutar los tests."
            # No salir aquí para permitir que los servicios sigan corriendo si los tests fallan
        }
    } else {
        Write-Host "Error al iniciar los servicios de Docker Compose."
        exit 1
    }
} else {
    Write-Host "Error al construir la imagen de Docker."
    exit 1
}

Write-Host ""
Write-Host "Configuración inicial completada."
Write-Host "Recuerda revisar y editar el resto de las configuraciones en el archivo .env."
