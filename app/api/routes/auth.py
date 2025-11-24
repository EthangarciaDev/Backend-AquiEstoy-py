from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
import bcrypt

router = APIRouter()

class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str

class RegisterRequest(BaseModel):
    idTipoUsuario: int
    nombres: str
    apellidoPaterno: str
    apellidoMaterno: str
    correo: EmailStr
    contrasena: str
    telefono: str
    direccion: str
    colonia: str
    codigoPostal: str
    ciudad: str
    estado: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    usuario: dict

@router.post("/login", response_model=LoginResponse)
async def iniciar_sesion(credentials: LoginRequest):
    """Endpoint para iniciar sesión"""
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()
        
        # Buscar usuario por correo
        query = "SELECT * FROM Usuarios WHERE correo = %s"
        cursor.execute(query, (credentials.correo,))
        usuario = cursor.fetchone()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos"
            )
        
        # Verificar si el usuario está activo
        if usuario.get('estaActivo') != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )
        
        # Verificar contraseña hasheada con bcrypt
        if not bcrypt.checkpw(credentials.contrasena.encode('utf-8'), usuario['contrasena'].encode('utf-8')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos"
            )
        
        # Eliminar contraseña de la respuesta
        usuario_respuesta = {k: v for k, v in usuario.items() if k != 'contrasena'}
        
        return {
            "success": True,
            "message": "Inicio de sesión exitoso",
            "usuario": usuario_respuesta
        }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el servidor: {str(e)}"
        )
    finally:
        if conexion:
            conexion.close()

@router.post("/register")
async def registrar_usuario(datos: RegisterRequest):
    """Endpoint para registrar un nuevo usuario"""
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()
        
        # Verificar si el correo ya existe
        query_verificar = "SELECT id FROM Usuarios WHERE correo = %s"
        cursor.execute(query_verificar, (datos.correo,))
        usuario_existente = cursor.fetchone()
        
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado"
            )
        
        # Hashear contraseña con bcrypt
        salt = bcrypt.gensalt()
        contrasena_hash = bcrypt.hashpw(datos.contrasena.encode('utf-8'), salt)
        contrasena_guardada = contrasena_hash.decode('utf-8')
        
        # Insertar nuevo usuario
        query_insertar = """
            INSERT INTO Usuarios (
                idTipoUsuario, nombres, apellidoPaterno, apellidoMaterno,
                correo, contrasena, telefono, direccion, colonia, codigoPostal,
                ciudad, estado, estaActivo, verificado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query_insertar, (
            datos.idTipoUsuario,
            datos.nombres,
            datos.apellidoPaterno,
            datos.apellidoMaterno,
            datos.correo,
            contrasena_guardada,
            datos.telefono,
            datos.direccion,
            datos.colonia,
            datos.codigoPostal,
            datos.ciudad,
            datos.estado,
            1,  # estaActivo
            0   # verificado
        ))
        
        conexion.commit()
        usuario_id = cursor.lastrowid
        
        # Obtener el usuario creado
        query_usuario = "SELECT * FROM Usuarios WHERE id = %s"
        cursor.execute(query_usuario, (usuario_id,))
        usuario_nuevo = cursor.fetchone()
        
        # Eliminar contraseña de la respuesta
        usuario_respuesta = {k: v for k, v in usuario_nuevo.items() if k != 'contrasena'}
        
        return {
            "success": True,
            "message": "Usuario registrado exitosamente",
            "usuario": usuario_respuesta
        }
            
    except HTTPException:
        raise
    except Exception as e:
        if conexion:
            conexion.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el servidor: {str(e)}"
        )
    finally:
        if conexion:
            conexion.close()

@router.post("/logout")
async def cerrar_sesion():
    """Endpoint para cerrar sesión (placeholder para cuando uses JWT)"""
    return {"success": True, "message": "Sesión cerrada exitosamente"}