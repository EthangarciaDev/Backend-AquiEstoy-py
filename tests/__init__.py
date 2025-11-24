# tests/__init__.py

# Ejemplo simple de funciones CRUD para testing

def crear_usuario(conexion, idTipoUsuario, nombres, apellidoPaterno, apellidoMaterno, 
                  correo, contrasena, telefono, direccion, colonia, codigoPostal, 
                  ciudad, estado, estaActivo=1, verificado=0):
    """Crear un nuevo usuario"""
    cursor = conexion.cursor()
    query = """
        INSERT INTO Usuarios (
            idTipoUsuario, nombres, apellidoPaterno, apellidoMaterno,
            correo, contrasena, telefono, direccion, colonia, codigoPostal,
            ciudad, estado, estaActivo, verificado
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        idTipoUsuario, nombres, apellidoPaterno, apellidoMaterno,
        correo, contrasena, telefono, direccion, colonia, codigoPostal,
        ciudad, estado, estaActivo, verificado
    ))
    conexion.commit()
    return cursor.lastrowid

def leer_usuario(conexion, usuario_id):
    """Leer un usuario por ID"""
    cursor = conexion.cursor()
    query = "SELECT * FROM Usuarios WHERE id = %s"
    cursor.execute(query, (usuario_id,))
    return cursor.fetchone()

def leer_todos_usuarios(conexion):
    """Leer todos los usuarios"""
    cursor = conexion.cursor()
    query = "SELECT * FROM Usuarios"
    cursor.execute(query)
    return cursor.fetchall()

def actualizar_usuario(conexion, usuario_id, **kwargs):
    """Actualizar un usuario existente - acepta cualquier campo como parámetro"""
    cursor = conexion.cursor()
    
    # Campos permitidos
    campos_permitidos = [
        'idTipoUsuario', 'nombres', 'apellidoPaterno', 'apellidoMaterno',
        'correo', 'contrasena', 'telefono', 'direccion', 'colonia',
        'codigoPostal', 'ciudad', 'estado', 'estaActivo', 'verificado'
    ]
    
    # Filtrar solo campos válidos
    campos_actualizar = {k: v for k, v in kwargs.items() if k in campos_permitidos and v is not None}
    
    if not campos_actualizar:
        return 0
    
    # Construir query dinámicamente
    set_clause = ", ".join([f"{campo} = %s" for campo in campos_actualizar.keys()])
    query = f"UPDATE Usuarios SET {set_clause} WHERE id = %s"
    
    valores = list(campos_actualizar.values()) + [usuario_id]
    cursor.execute(query, valores)
    conexion.commit()
    return cursor.rowcount

def eliminar_usuario(conexion, usuario_id):
    """Eliminar un usuario"""
    cursor = conexion.cursor()
    query = "DELETE FROM Usuarios WHERE id = %s"
    cursor.execute(query, (usuario_id,))
    conexion.commit()
    return cursor.rowcount
