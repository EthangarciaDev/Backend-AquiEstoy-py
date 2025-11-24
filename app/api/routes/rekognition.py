# app/api/routes/rekognition.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.rekognition_service import RekognitionService

router = APIRouter()
rekognition_service = RekognitionService()

@router.post("/detect-faces")
async def detect_faces(file: UploadFile = File(...)):
    """Detectar rostros en una imagen"""
    try:
        result = await rekognition_service.detect_faces(file)
        return {"faces_detected": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
