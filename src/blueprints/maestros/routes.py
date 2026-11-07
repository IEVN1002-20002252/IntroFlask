from flask import Blueprint, jsonify, request
from database import mysql 

maestros_bp = Blueprint(
    'maestros',
    __name__,
    url_prefix='/api/maestros'
)

def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.description]
    return dict(zip(columnas, fila))

def leer_maestro_bd(idmaestro):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM maestros WHERE idmaestro = %s", (idmaestro,))
        datos = cursor.fetchone()
        if datos:
            return fila_a_diccionario(cursor, datos)
        return None
    except Exception as ex:
        raise ex
    finally:
        if cursor is not None:
            cursor.close()

# 1. LISTAR TODOS (GET)
@maestros_bp.route("/", methods=['GET'])
def listar_maestros():
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM maestros")
        datos = cursor.fetchall()
        maestros = [fila_a_diccionario(cursor, fila) for fila in datos]
        return jsonify({
            'maestros': maestros,
            'mensaje': 'Lista de maestros',
            'exito': True
        }), 200
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {ex}', 'exito': False}), 500
    finally:
        if cursor is not None:
            cursor.close()

# 2. OBTENER UN MAESTRO (GET)
@maestros_bp.route("/<id>", methods=['GET'])
def leer_maestro(id):
    try:
        maestro = leer_maestro_bd(id)
        if maestro:
            return jsonify({'maestro': maestro, 'mensaje': 'Maestro encontrado', 'exito': True}), 200
        else:
            return jsonify({'maestro': {}, 'mensaje': 'Maestro no encontrado', 'exito': False}), 404
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {ex}', 'exito': False}), 500

# 3. REGISTRAR MAESTRO (POST)
@maestros_bp.route("/", methods=['POST'])
def registra_maestro():
    cursor = None
    try:
        data = request.json
        idmaestro = data.get('idmaestro')
        
        if leer_maestro_bd(idmaestro):
            return jsonify({'mensaje': 'El maestro ya existe', 'exito': False}), 400

        cursor = mysql.connection.cursor()
        sql = """INSERT INTO maestros (idmaestro, nombre, apaterno, amaterno, correo) 
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (
            idmaestro,
            data.get('nombre'),
            data.get('apaterno'),
            data.get('amaterno'),
            data.get('correo')
        ))
        mysql.connection.commit()
        return jsonify({'mensaje': 'Maestro registrado con éxito', 'exito': True}), 201
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {ex}', 'exito': False}), 500
    finally:
        if cursor is not None:
            cursor.close()

# 4. ACTUALIZAR MAESTRO (PUT)
@maestros_bp.route("/<id>", methods=['PUT'])
def actualizar_maestro(id):
    cursor = None
    try:
        if not leer_maestro_bd(id):
            return jsonify({'mensaje': 'Maestro no encontrado', 'exito': False}), 404

        data = request.json
        cursor = mysql.connection.cursor()
        sql = """UPDATE maestros SET nombre = %s, apaterno = %s, amaterno = %s, correo = %s 
                 WHERE idmaestro = %s"""
        cursor.execute(sql, (
            data.get('nombre'),
            data.get('apaterno'),
            data.get('amaterno'),
            data.get('correo'),
            id
        ))
        mysql.connection.commit()
        return jsonify({'mensaje': 'Maestro actualizado con éxito', 'exito': True}), 200
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {ex}', 'exito': False}), 500
    finally:
        if cursor is not None:
            cursor.close()

# 5. ELIMINAR MAESTRO (DELETE)
@maestros_bp.route("/<id>", methods=['DELETE'])
def eliminar_maestro(id):
    cursor = None
    try:
        if not leer_maestro_bd(id):
            return jsonify({'mensaje': 'Maestro no encontrado', 'exito': False}), 404

        cursor = mysql.connection.cursor()
        sql = "DELETE FROM maestros WHERE idmaestro = %s"
        cursor.execute(sql, (id,))
        mysql.connection.commit()
        return jsonify({'mensaje': 'Maestro eliminado con éxito', 'exito': True}), 200
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {ex}', 'exito': False}), 500
    finally:
        if cursor is not None:
            cursor.close()