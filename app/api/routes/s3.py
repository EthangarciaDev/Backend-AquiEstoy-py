# app/api/routes/s3.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.s3_service import S3Service

router = APIRouter()
s3_service = S3Service()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Subir archivo a S3"""
    try:
        file_url = await s3_service.upload_file(file)
        return {"message": "Archivo subido exitosamente", "url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
