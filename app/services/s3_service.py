# app/services/s3_service.py
from fastapi import UploadFile
from app.core.aws_clients import aws_clients
from app.core.config import settings

class S3Service:
    """Servicio para operaciones con S3"""
    
    def __init__(self):
        self.s3_client = aws_clients.s3
        self.bucket_name = settings.S3_BUCKET_NAME
    
    async def upload_file(self, file: UploadFile) -> str:
        """Subir archivo a S3 y retornar la URL"""
        try:
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                file.filename
            )
            
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file.filename}"
            return file_url
        except Exception as e:
            raise Exception(f"Error al subir archivo a S3: {str(e)}")
    
    async def delete_file(self, filename: str) -> bool:
        """Eliminar archivo de S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=filename)
            return True
        except Exception as e:
            raise Exception(f"Error al eliminar archivo de S3: {str(e)}")
