# app/api/routes/health.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from tests import crear_usuario, leer_usuario, leer_todos_usuarios, actualizar_usuario, eliminar_usuario
from app.core.database import get_db


router = APIRouter()

class UsuarioCreate(BaseModel):
    idTipoUsuario: int
    nombres: str
    apellidoPaterno: str
    apellidoMaterno: str
    correo: str
    contrasena: str
    telefono: str
    direccion: str
    colonia: str
    codigoPostal: str
    ciudad: str
    estado: str
    estaActivo: int = 1
    verificado: int = 0

class UsuarioUpdate(BaseModel):
    idTipoUsuario: Optional[int] = None
    nombres: Optional[str] = None
    apellidoPaterno: Optional[str] = None
    apellidoMaterno: Optional[str] = None
    correo: Optional[str] = None
    contrasena: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    colonia: Optional[str] = None
    codigoPostal: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    estaActivo: Optional[int] = None
    verificado: Optional[int] = None

@router.post("/test/crear")
async def test_crear_usuario(usuario: UsuarioCreate):
    """Crear usuario de prueba"""
    conexion = None
    try:
        conexion = get_db()
        usuario_id = crear_usuario(
            conexion, 
            usuario.idTipoUsuario,
            usuario.nombres,
            usuario.apellidoPaterno,
            usuario.apellidoMaterno,
            usuario.correo,
            usuario.contrasena,
            usuario.telefono,
            usuario.direccion,
            usuario.colonia,
            usuario.codigoPostal,
            usuario.ciudad,
            usuario.estado,
            usuario.estaActivo,
            usuario.verificado
        )
        
        return {"success": True, "usuario_id": usuario_id, "message": "Usuario creado"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if conexion:
            conexion.close()

@router.get("/test/leer/{usuario_id}")
async def test_leer_usuario(usuario_id: int):
    """Leer usuario de prueba por ID"""
    conexion = None
    try:
        conexion = get_db()
        usuario = leer_usuario(conexion, usuario_id)
        
        if usuario:
            return {"success": True, "data": usuario}
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if conexion:
            conexion.close()

@router.get("/test/leer")
async def test_leer_todos_usuarios():
    """Leer todos los usuarios"""
    conexion = None
    try:
        conexion = get_db()
        usuarios = leer_todos_usuarios(conexion)
        
        return {"success": True, "total": len(usuarios), "data": usuarios}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if conexion:
            conexion.close()

@router.put("/test/actualizar/{usuario_id}")
async def test_actualizar_usuario(usuario_id: int, usuario: UsuarioUpdate):
    """Actualizar usuario de prueba"""
    conexion = None
    try:
        conexion = get_db()
        
        # Convertir el modelo a diccionario, excluyendo valores None
        datos_actualizar = usuario.model_dump(exclude_unset=True)
        
        if not datos_actualizar:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        
        filas_actualizadas = actualizar_usuario(conexion, usuario_id, **datos_actualizar)
        
        if filas_actualizadas > 0:
            # Obtener el usuario actualizado
            usuario_actualizado = leer_usuario(conexion, usuario_id)
            return {
                "success": True, 
                "message": f"Usuario {usuario_id} actualizado correctamente",
                "data": usuario_actualizado
            }
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if conexion:
            conexion.close()

@router.delete("/test/eliminar/{usuario_id}")
async def test_eliminar_usuario(usuario_id: int):
    """Eliminar usuario de prueba"""
    conexion = None
    try:
        conexion = get_db()
        filas_eliminadas = eliminar_usuario(conexion, usuario_id)
        
        if filas_eliminadas > 0:
            return {"success": True, "message": f"Usuario {usuario_id} eliminado correctamente"}
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if conexion:
            conexion.close()