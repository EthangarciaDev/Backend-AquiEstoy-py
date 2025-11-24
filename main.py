# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import health, s3, rekognition, test, auth, casos

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(casos.router, prefix="/casos", tags=["Casos"])
app.include_router(s3.router, prefix="/s3", tags=["S3"])
app.include_router(rekognition.router, prefix="/rekognition", tags=["Rekognition"])
app.include_router(test.router, prefix="/api", tags=["Test"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)