# main.py (Ejemplo con FastAPI y Boto3)
from fastapi import FastAPI
import boto3
import os

# 1. Cargar Variables de Entorno (Opcional, pero recomendado en desarrollo)
# Debes configurar las credenciales de AWS aquí.
# En producción, AWS las inyectará automáticamente a tu servicio.
# En desarrollo local: export AWS_ACCESS_KEY_ID=... y export AWS_SECRET_ACCESS_KEY=...

app = FastAPI()

# 2. Inicializar los clientes de AWS
# Boto3 leerá automáticamente las credenciales de tus variables de entorno.
s3_client = boto3.client('s3', region_name=os.environ.get("AWS_REGION", "us-east-1"))
rekognition_client = boto3.client('rekognition', region_name=os.environ.get("AWS_REGION", "us-east-1"))

@app.get("/")
def read_root():
    return {"Hello": "Backend en Python listo para AWS"}

# Aquí irán tus rutas para RDS, S3 y Rekognition.
# Ejemplo de ruta para S3:
# @app.post("/upload")
# def upload_file_to_s3(file: UploadFile = File(...)):
#     s3_client.upload_fileobj(file.file, "mi-bucket-de-s3", file.filename)
#     return {"message": "File uploaded"}