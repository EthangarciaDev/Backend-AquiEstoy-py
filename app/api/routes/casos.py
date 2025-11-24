from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.core.database import get_db
import boto3
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

router = APIRouter()

# Configuración de AWS S3
s3_client = boto3.client(
    's3',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

class CasoCreate(BaseModel):
    idBeneficiario: int
    idCategoria: int
    titulo: str
    descripcion: str
    montoObjetivo: float
    entidad: str
    direccion: str
    fechaLimite: datetime

class CasoUpdate(BaseModel):
    idCategoria: Optional[int] = None
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    montoObjetivo: Optional[float] = None
    entidad: Optional[str] = None
    direccion: Optional[str] = None
    fechaLimite: Optional[datetime] = None
    idEstado: Optional[int] = None
    estaAbierto: Optional[int] = None

class CasoResponse(BaseModel):
    success: bool
    message: str
    caso_id: int
    data: dict

def traducir_estado(id_estado: int) -> str:
    """Traduce el ID del estado a texto legible"""
    estados = {
        1: "Activo",
        2: "En Revisión",
        3: "Pausado",
        4: "Rechazado",
        5: "Concluido"
    }
    return estados.get(id_estado, "Desconocido")

def traducir_esta_abierto(esta_abierto: int) -> str:
    """Traduce si el caso está abierto o cerrado"""
    return "Abierto" if esta_abierto == 1 else "Cerrado"

def subir_imagen_s3(archivo: UploadFile, caso_id: int, numero_imagen: int) -> str:
    """Sube una imagen a S3 y retorna la URL"""
    try:
        # Generar nombre único para la imagen
        extension = archivo.filename.split('.')[-1]
        nombre_archivo = f"casos/caso_{caso_id}/imagen_{numero_imagen}_{uuid.uuid4()}.{extension}"
        
        # Subir a S3
        s3_client.upload_fileobj(
            archivo.file,
            S3_BUCKET_NAME,
            nombre_archivo,
            ExtraArgs={'ContentType': archivo.content_type}
        )
        
        # Generar URL pública
        url = f"https://{S3_BUCKET_NAME}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{nombre_archivo}"
        return url
    except Exception as e:
        raise Exception(f"Error al subir imagen a S3: {str(e)}")

def formatear_caso(caso: dict) -> dict:
    """Formatea un caso con información estructurada"""
    return {
        "id": caso.get("id"),
        "titulo": caso.get("titulo"),
        "descripcion": caso.get("descripcion"),
        "montoObjetivo": caso.get("montoObjetivo"),
        "montoRecaudado": caso.get("montoRecaudado", 0),
        "entidad": caso.get("entidad"),
        "direccion": caso.get("direccion"),
        "fechaLimite": caso.get("fechaLimite"),
        "fechaCreacion": caso.get("fechaCreacion"),
        "imagenes": {
            "imagen1": caso.get("imagen1"),
            "imagen2": caso.get("imagen2"),
            "imagen3": caso.get("imagen3"),
            "imagen4": caso.get("imagen4")
        },
        "estado": {
            "id": caso.get("idEstado"),
            "nombre": traducir_estado(caso.get("idEstado"))
        },
        "estadoApertura": {
            "valor": caso.get("estaAbierto"),
            "nombre": traducir_esta_abierto(caso.get("estaAbierto", 1))
        },
        "categoria": {
            "id": caso.get("idCategoria"),
            "nombre": caso.get("nombreCategoria")
        },
        "beneficiario": {
            "id": caso.get("idBeneficiario"),
            "nombres": caso.get("nombreBeneficiario"),
            "apellidoPaterno": caso.get("apellidoBeneficiario"),
            "apellidoMaterno": caso.get("apellidoMaterno"),
            "nombreCompleto": f"{caso.get('nombreBeneficiario', '')} {caso.get('apellidoBeneficiario', '')} {caso.get('apellidoMaterno', '')}".strip(),
            "correo": caso.get("correoBeneficiario"),
            "telefono": caso.get("telefonoBeneficiario")
        }
    }

@router.post("/crear")
async def crear_caso(
    idBeneficiario: int = Form(...),
    idCategoria: int = Form(...),
    titulo: str = Form(...),
    descripcion: str = Form(...),
    montoObjetivo: float = Form(...),
    entidad: str = Form(...),
    direccion: str = Form(...),
    fechaLimite: str = Form(...),
    imagen1: UploadFile = File(None),
    imagen2: UploadFile = File(None),
    imagen3: UploadFile = File(None),
    imagen4: UploadFile = File(None)
):
    """
    Endpoint para crear un nuevo caso con hasta 4 imágenes.
    Las imágenes se suben a S3 y se guardan las URLs en la base de datos.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()
        
        # Iniciar transacción
        conexion.begin()
        
        # Convertir fechaLimite de string a datetime
        fecha_limite_dt = datetime.fromisoformat(fechaLimite.replace('Z', '+00:00'))
        
        # Paso 1: Insertar el Caso Principal (sin imágenes primero)
        query_caso = """
            INSERT INTO Casos (
                idBeneficiario,
                idEstado,
                titulo,
                descripcion,
                montoObjetivo,
                entidad,
                direccion,
                fechaLimite
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query_caso, (
            idBeneficiario,
            1,  # Estado inicial: Activo
            titulo,
            descripcion,
            montoObjetivo,
            entidad,
            direccion,
            fecha_limite_dt
        ))
        
        # Obtener el ID del caso recién creado
        caso_id = cursor.lastrowid
        
        # Paso 2: Subir imágenes a S3 y obtener URLs
        urls_imagenes = {}
        imagenes = [
            (imagen1, 1, 'imagen1'),
            (imagen2, 2, 'imagen2'),
            (imagen3, 3, 'imagen3'),
            (imagen4, 4, 'imagen4')
        ]
        
        for imagen, numero, campo in imagenes:
            if imagen and imagen.filename:
                url = subir_imagen_s3(imagen, caso_id, numero)
                urls_imagenes[campo] = url
        
        # Paso 3: Actualizar el caso con las URLs de las imágenes
        if urls_imagenes:
            campos_update = ", ".join([f"{campo} = %s" for campo in urls_imagenes.keys()])
            query_imagenes = f"UPDATE Casos SET {campos_update} WHERE id = %s"
            valores = list(urls_imagenes.values()) + [caso_id]
            cursor.execute(query_imagenes, valores)
        
        # Paso 4: Asignar la Categoría al Caso
        query_categoria = """
            INSERT INTO CasoCategorias (
                idCaso,
                idCategoria
            ) VALUES (%s, %s)
        """
        
        cursor.execute(query_categoria, (caso_id, idCategoria))
        
        # Confirmar la transacción
        conexion.commit()
        
        # Obtener el caso completo creado
        query_obtener = """
            SELECT 
                c.*,
                cc.idCategoria,
                cat.nombre as nombreCategoria,
                u.nombres as nombreBeneficiario,
                u.apellidoPaterno as apellidoBeneficiario,
                u.apellidoMaterno as apellidoMaterno,
                u.correo as correoBeneficiario,
                u.telefono as telefonoBeneficiario
            FROM Casos c
            LEFT JOIN CasoCategorias cc ON c.id = cc.idCaso
            LEFT JOIN Categorias cat ON cc.idCategoria = cat.id
            LEFT JOIN Usuarios u ON c.idBeneficiario = u.id
            WHERE c.id = %s
        """
        cursor.execute(query_obtener, (caso_id,))
        caso_creado = cursor.fetchone()
        
        return {
            "success": True,
            "message": "Caso creado exitosamente con imágenes",
            "caso_id": caso_id,
            "imagenes_subidas": len(urls_imagenes),
            "data": formatear_caso(caso_creado)
        }
        
    except Exception as e:
        # Si algo falla, revertir la transacción
        if conexion:
            conexion.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el caso: {str(e)}"
        )
    finally:
        if conexion:
            conexion.close()

@router.get("/listar")
async def listar_casos():
    """Listar todos los casos con sus categorías"""
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()
        
        query = """
            SELECT 
                c.*,
                cc.idCategoria,
                cat.nombre as nombreCategoria,
                u.nombres as nombreBeneficiario,
                u.apellidoPaterno as apellidoBeneficiario,
                u.apellidoMaterno as apellidoMaterno,
                u.correo as correoBeneficiario,
                u.telefono as telefonoBeneficiario
            FROM Casos c
            LEFT JOIN CasoCategorias cc ON c.id = cc.idCaso
            LEFT JOIN Categorias cat ON cc.idCategoria = cat.id
            LEFT JOIN Usuarios u ON c.idBeneficiario = u.id
            ORDER BY c.fechaCreacion DESC
        """
        
        cursor.execute(query)
        casos = cursor.fetchall()
        
        # Formatear cada caso
        casos_formateados = [formatear_caso(caso) for caso in casos]
        
        return {
            "success": True,
            "total": len(casos_formateados),
            "data": casos_formateados
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar casos: {str(e)}"
        )
    finally:
        if conexion:
            conexion.close()

@router.get("/obtener/{caso_id}")
async def obtener_caso(caso_id: int):
    """Obtener un caso específico por ID con formato estructurado"""
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()
        
        query = """
            SELECT 
                c.*,
                cc.idCategoria,
                cat.nombre as nombreCategoria,
                u.nombres as nombreBeneficiario,
                u.apellidoPaterno as apellidoBeneficiario,
                u.apellidoMaterno as apellidoMaterno,
                u.correo as correoBeneficiario,
                u.telefono as telefonoBeneficiario
            FROM Casos c
            LEFT JOIN CasoCategorias cc ON c.id = cc.idCaso
            LEFT JOIN Categorias cat ON cc.idCategoria = cat.id
            LEFT JOIN Usuarios u ON c.idBeneficiario = u.id
            WHERE c.id = %s
        """
        
        cursor.execute(query, (caso_id,))
        caso = cursor.fetchone()
        
        if not caso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caso no encontrado"
            )
        
        return {
            "success": True,
            "data": formatear_caso(caso)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el caso: {str(e)}"
        )
    finally:
        if conexion:
            conexion.close()

@router.put("/actualizar/{caso_id}")
async def actualizar_caso(caso_id: int, datos: CasoUpdate):
    """Actualizar un caso existente con transacciones"""
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()
        
        # Verificar que el caso existe
        query_verificar = "SELECT id FROM Casos WHERE id = %s"
        cursor.execute(query_verificar, (caso_id,))
        caso_existe = cursor.fetchone()
        
        if not caso_existe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caso no encontrado"
            )
        
        # Iniciar transacción
        conexion.begin()
        
        # Preparar campos a actualizar en Casos
        campos_caso = {}
        if datos.titulo is not None:
            campos_caso['titulo'] = datos.titulo
        if datos.descripcion is not None:
            campos_caso['descripcion'] = datos.descripcion
        if datos.montoObjetivo is not None:
            campos_caso['montoObjetivo'] = datos.montoObjetivo
        if datos.entidad is not None:
            campos_caso['entidad'] = datos.entidad
        if datos.direccion is not None:
            campos_caso['direccion'] = datos.direccion
        if datos.fechaLimite is not None:
            campos_caso['fechaLimite'] = datos.fechaLimite
        if datos.idEstado is not None:
            campos_caso['idEstado'] = datos.idEstado
        if datos.estaAbierto is not None:
            campos_caso['estaAbierto'] = datos.estaAbierto
        
        # Actualizar campos del caso si hay cambios
        if campos_caso:
            set_clause = ", ".join([f"{campo} = %s" for campo in campos_caso.keys()])
            query_caso = f"UPDATE Casos SET {set_clause} WHERE id = %s"
            valores_caso = list(campos_caso.values()) + [caso_id]
            cursor.execute(query_caso, valores_caso)
        
        # Actualizar categoría si se proporciona
        if datos.idCategoria is not None:
            # Verificar si ya existe una categoría asignada
            query_verificar_cat = "SELECT id FROM CasoCategorias WHERE idCaso = %s"
            cursor.execute(query_verificar_cat, (caso_id,))
            categoria_existe = cursor.fetchone()
            
            if categoria_existe:
                # Actualizar categoría existente
                query_actualizar_cat = "UPDATE CasoCategorias SET idCategoria = %s WHERE idCaso = %s"
                cursor.execute(query_actualizar_cat, (datos.idCategoria, caso_id))
            else:
                # Insertar nueva categoría
                query_insertar_cat = "INSERT INTO CasoCategorias (idCaso, idCategoria) VALUES (%s, %s)"
                cursor.execute(query_insertar_cat, (caso_id, datos.idCategoria))
        
        # Confirmar la transacción
        conexion.commit()
        
        # Obtener el caso actualizado
        query_obtener = """
            SELECT 
                c.*,
                cc.idCategoria,
                cat.nombre as nombreCategoria,
                u.nombres as nombreBeneficiario,
                u.apellidoPaterno as apellidoBeneficiario,
                u.apellidoMaterno as apellidoMaterno,
                u.correo as correoBeneficiario,
                u.telefono as telefonoBeneficiario
            FROM Casos c
            LEFT JOIN CasoCategorias cc ON c.id = cc.idCaso
            LEFT JOIN Categorias cat ON cc.idCategoria = cat.id
            LEFT JOIN Usuarios u ON c.idBeneficiario = u.id
            WHERE c.id = %s
        """
        cursor.execute(query_obtener, (caso_id,))
        caso_actualizado = cursor.fetchone()
        
        return {
            "success": True,
            "message": "Caso actualizado exitosamente",
            "data": formatear_caso(caso_actualizado)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if conexion:
            conexion.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el caso: {str(e)}"
        )
    finally:
        if conexion:
            conexion.close()

@router.delete("/eliminar/{caso_id}")
async def eliminar_caso(caso_id: int):
    """Eliminar un caso y su categoría asociada con transacciones"""
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()
        
        # Verificar que el caso existe
        query_verificar = "SELECT id, titulo FROM Casos WHERE id = %s"
        cursor.execute(query_verificar, (caso_id,))
        caso = cursor.fetchone()
        
        if not caso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caso no encontrado"
            )
        
        # Iniciar transacción
        conexion.begin()
        
        # Eliminar relaciones en CasoCategorias primero (clave foránea)
        query_eliminar_categorias = "DELETE FROM CasoCategorias WHERE idCaso = %s"
        cursor.execute(query_eliminar_categorias, (caso_id,))
        
        # Eliminar el caso
        query_eliminar_caso = "DELETE FROM Casos WHERE id = %s"
        cursor.execute(query_eliminar_caso, (caso_id,))
        
        # Confirmar la transacción
        conexion.commit()
        
        return {
            "success": True,
            "message": f"Caso '{caso.get('titulo')}' eliminado exitosamente",
            "caso_id": caso_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if conexion:
            conexion.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el caso: {str(e)}"
        )
    finally:
        if conexion:
            conexion.close()