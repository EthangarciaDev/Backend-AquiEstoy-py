# app/api/routes/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "ok", "message": "Backend-AquiEstoy funcionando correctamente"}
