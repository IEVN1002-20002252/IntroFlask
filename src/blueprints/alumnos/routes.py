from flask import Blueprint, jsonify, request
from database import mysql 

alumnos_bp = Blueprint(
    'alumnos',
    __name__,
    url_prefix='/api/alumnos'
)

def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.description]
    return dict(zip(columnas, fila))

def leer_alumno_bd(matricula):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM alumnos WHERE matricula = %s", (matricula,))
        datos = cursor.fetchone()
        if datos:
            return fila_a_diccionario(cursor, datos)
        return None
    except Exception as ex:
        raise ex
    finally:
        if cursor is not None:
            cursor.close()

# 1. LISTAR TODOS (GET) -> /api/alumnos/
@alumnos_bp.route("/", methods=['GET'])
def listar_alumnos():
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM alumnos")
        datos = cursor.fetchall()
        alumnos = [fila_a_diccionario(cursor, fila) for fila in datos]
        return jsonify({
            'alumnos': alumnos,
            'mensaje': 'Lista de alumnos',
            'exito': True
        }), 200
    except Exception as ex:
        return jsonify({
            'mensaje': f'Error: {ex}',
            'exito': False
        }), 500
    finally:
        if cursor is not None:
            cursor.close()

# 2. OBTENER UN ALUMNO POR MATRÍCULA (GET) -> /api/alumnos/<mat>
@alumnos_bp.route("/<mat>", methods=['GET'])
def leer_alumno(mat):
    try:
        alumno = leer_alumno_bd(mat)
        if alumno:
            return jsonify({'alumno': alumno, 'mensaje': 'Alumno encontrado', 'exito': True}), 200
        else:
            return jsonify({'alumno': {}, 'mensaje': 'Alumno no encontrado', 'exito': False}), 404
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {ex}', 'exito': False}), 500

# 3. REGISTRAR ALUMNO (POST) -> /api/alumnos/
@alumnos_bp.route("/", methods=['POST'])
def registra_alumno():
    cursor = None
    try:
        data = request.json
        matricula = data.get('matricula')
        
        if leer_alumno_bd(matricula):
            return jsonify({'mensaje': 'El alumno ya existe', 'exito': False}), 400

        cursor = mysql.connection.cursor()
        sql = """INSERT INTO alumnos (matricula, nombre, apaterno, amaterno, correo) 
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (
            matricula,
            data.get('nombre'),
            data.get('apaterno'),
            data.get('amaterno'),
            data.get('correo')
        ))
        mysql.connection.commit()
        return jsonify({'mensaje': 'Alumno registrado con éxito', 'exito': True}), 201
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {ex}', 'exito': False}), 500
    finally:
        if cursor is not None:
            cursor.close()

# 4. ACTUALIZAR ALUMNO (PUT) -> /api/alumnos/<mat>
@alumnos_bp.route("/<mat>", methods=['PUT'])
def actualizar_alumno(mat):
    cursor = None
    try:
        if not leer_alumno_bd(mat):
            return jsonify({'mensaje': 'Alumno no encontrado', 'exito': False}), 404

        data = request.json
        cursor = mysql.connection.cursor()
        sql = """UPDATE alumnos SET nombre = %s, apaterno = %s, amaterno = %s, correo = %s 
                 WHERE matricula = %s"""
        cursor.execute(sql, (
            data.get('nombre'),
            data.get('apaterno'),
            data.get('amaterno'),
            data.get('correo'),
            mat
        ))
        mysql.connection.commit()
        return jsonify({'mensaje': 'Alumno actualizado con éxito', 'exito': True}), 200
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {ex}', 'exito': False}), 500
    finally:
        if cursor is not None:
            cursor.close()

# 5. ELIMINAR ALUMNO (DELETE) -> /api/alumnos/<mat>
@alumnos_bp.route("/<mat>", methods=['DELETE'])
def eliminar_alumno(mat):
    cursor = None
    try:
        if not leer_alumno_bd(mat):
            return jsonify({'mensaje': 'Alumno no encontrado', 'exito': False}), 404

        cursor = mysql.connection.cursor()
        sql = "DELETE FROM alumnos WHERE matricula = %s"
        cursor.execute(sql, (mat,))
        mysql.connection.commit()
        return jsonify({'mensaje': 'Alumno eliminado con éxito', 'exito': True}), 200
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {ex}', 'exito': False}), 500
    finally:
        if cursor is not None:
            cursor.close()