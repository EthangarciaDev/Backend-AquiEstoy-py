# app/services/rekognition_service.py
from fastapi import UploadFile
from app.core.aws_clients import aws_clients

class RekognitionService:
    """Servicio para operaciones con Rekognition"""
    
    def __init__(self):
        self.rekognition_client = aws_clients.rekognition
    
    async def detect_faces(self, file: UploadFile) -> dict:
        """Detectar rostros en una imagen"""
        try:
            image_bytes = await file.read()
            
            response = self.rekognition_client.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']
            )
            
            return {
                "faces_count": len(response['FaceDetails']),
                "faces": response['FaceDetails']
            }
        except Exception as e:
            raise Exception(f"Error al detectar rostros: {str(e)}")
    
    async def compare_faces(self, source_image: UploadFile, target_image: UploadFile) -> dict:
        """Comparar dos rostros"""
        try:
            source_bytes = await source_image.read()
            target_bytes = await target_image.read()
            
            response = self.rekognition_client.compare_faces(
                SourceImage={'Bytes': source_bytes},
                TargetImage={'Bytes': target_bytes}
            )
            
            return response
        except Exception as e:
            raise Exception(f"Error al comparar rostros: {str(e)}")
