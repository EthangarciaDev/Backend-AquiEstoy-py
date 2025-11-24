# Backend AquiEstoy

Backend en Python con FastAPI y AWS (S3, Rekognition, RDS)

## 📁 Estructura del Proyecto

```
Backend-AquiEstoy-py/
├── app/
│   ├── __init__.py
│   ├── api/                    # Capa de API
│   │   ├── __init__.py
│   │   └── routes/             # Endpoints
│   │       ├── __init__.py
│   │       ├── health.py       # Health check
│   │       ├── s3.py          # Rutas de S3
│   │       └── rekognition.py # Rutas de Rekognition
│   ├── core/                   # Configuración core
│   │   ├── __init__.py
│   │   ├── config.py          # Variables de configuración
│   │   └── aws_clients.py     # Clientes AWS
│   ├── models/                 # Modelos de base de datos
│   │   └── __init__.py
│   ├── schemas/                # Schemas Pydantic (DTOs)
│   │   └── __init__.py
│   └── services/               # Lógica de negocio
│       ├── __init__.py
│       ├── s3_service.py      # Servicio S3
│       └── rekognition_service.py # Servicio Rekognition
├── tests/                      # Tests unitarios
│   └── __init__.py
├── main.py                     # Punto de entrada
├── requirements.txt            # Dependencias
├── .env.example               # Ejemplo de variables de entorno
├── .gitignore                 # Archivos ignorados por git
└── README.md                  # Este archivo
```

## 🚀 Instalación

1. Clonar el repositorio
2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Edita .env con tus credenciales
```

## ▶️ Ejecutar el Proyecto

```bash
python main.py
```

O con uvicorn directamente:
```bash
uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

## 📦 Dependencias Principales

- **FastAPI**: Framework web
- **Uvicorn**: Servidor ASGI
- **Boto3**: SDK de AWS para Python
- **Pydantic**: Validación de datos
- **Python-multipart**: Para subida de archivos

## 🔧 Configuración AWS

Asegúrate de tener configuradas las siguientes variables de entorno:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `S3_BUCKET_NAME`

## 📝 Endpoints Disponibles

### Health Check
- `GET /` - Verificar estado del servidor

### S3
- `POST /s3/upload` - Subir archivo a S3

### Rekognition
- `POST /rekognition/detect-faces` - Detectar rostros en imagen
