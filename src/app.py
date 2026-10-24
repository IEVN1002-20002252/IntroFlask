from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from config import config
import math

app = Flask(__name__)

# Configurar la conexión a la base de datos usando config.py
app.config.from_object(config['development'])
conexion = MySQL(app)

# Creacion de rutas

@app.route("/")
def index():
    titulo = 'hola!'
    lista = ['luis', 'manuel', 'jesus']
    return render_template("index.html", titulo=titulo, lista=lista)

@app.route("/distancia", methods=["GET", "POST"])
def distancia():
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    res_distancia = 0
    
    if request.method == "POST":
        x1 = float(request.form.get("x1")) if request.form.get("x1") else 0
        y1 = float(request.form.get("y1")) if request.form.get("y1") else 0
        x2 = float(request.form.get("x2")) if request.form.get("x2") else 0
        y2 = float(request.form.get("y2")) if request.form.get("y2") else 0
        
        # Fórmula de distancia entre dos puntos
        res_distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    return render_template("distancia.html", x1=x1, y1=y1, x2=x2, y2=y2, res_distancia=res_distancia)

@app.route("/operasbas", methods=["GET", "POST"])
def operasbas():
    n1 = 0
    n2 = 0
    res = 0
    operacion = ""
    if request.method == "POST":
        n1 = request.form.get("n1")
        n2 = request.form.get("n2")
        if request.form.get("operacion") == "suma":
            res = float(n1) + float(n2)

    return render_template("operasbas.html", n1=n1, n2=n2, res=res)

@app.route("/alumnos", methods=['GET'])
def lista_alumnos():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM alumnos"
        cursor.execute(sql)
        datos = cursor.fetchall()
        alumnos = []
        for fila in datos:
            alumno = {
                "matricula": fila[0],
                "nombre": fila[1],
                "apaterno": fila[2],
                "amaterno": fila[3],
                "correo": fila[4]
            }
            alumnos.append(alumno)
        return jsonify({'alumnos': alumnos, 'mensaje': 'Lista de alumnos', 'exito': True})

    except Exception as ex:
        return jsonify({"message": "error {}".format(ex), 'exito': False})

def leer_alumno_bd(matricula):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM alumnos WHERE matricula = '{0}'".format(matricula)
        cursor.execute(sql)
        datos = cursor.fetchone()
        if datos != None:
            alumno = {
                "matricula": datos[0],
                "nombre": datos[1],
                "apaterno": datos[2],
                "amaterno": datos[3],
                "correo": datos[4]
            }
            return alumno
        else:
            return None
    except Exception as ex:
        raise ex

@app.route("/alumnos/<mat>", methods=['GET'])
def leer_alumno(mat):
    try:
        alumno = leer_alumno_bd(mat)
        if alumno != None:
            return jsonify({'alumno': alumno, 'mensaje': 'Alumno encontrado', 'exito': True})
        else:
            return jsonify({'alumno': {}, 'mensaje': 'Alumno no encontrado', 'exito': False})
    except Exception as ex:
        return jsonify({"message": "error {}".format(ex), 'exito': False})

@app.route("/alumnos", methods=['POST'])
def registra_alumno():
    try:
        alumno = leer_alumno_bd(request.json['matricula'])
        if alumno != None:
            return jsonify({"message": "Alumno ya existe", 'exito': False})
        else:
            cursor = conexion.connection.cursor()
            sql = """INSERT INTO alumnos (matricula, nombre, apaterno, amaterno, correo) 
                     VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')""".format(
                request.json['matricula'],
                request.json['nombre'],
                request.json['apaterno'],
                request.json['amaterno'],
                request.json['correo']
            )
            cursor.execute(sql)
            conexion.connection.commit()
            return jsonify({'mensaje': 'Alumno registrado', 'exito': True})
            
    except Exception as ex:
        return jsonify({'mensaje': "Error", 'exito': False})

@app.route("/alumnos/<mat>", methods=['PUT'])
def actualizar_alumno(mat):
    try:
        alumno = leer_alumno_bd(mat)
        if alumno != None:
            cursor = conexion.connection.cursor()
            sql = """UPDATE alumnos SET nombre = '{0}', apaterno = '{1}', amaterno = '{2}', correo = '{3}' 
                     WHERE matricula = '{4}'""".format(
                request.json['nombre'],
                request.json['apaterno'],
                request.json['amaterno'],
                request.json['correo'],
                mat
            )
            cursor.execute(sql)
            conexion.connection.commit()
            return jsonify({'mensaje': 'Alumno actualizado.', 'exito': True})
        else:
            return jsonify({'mensaje': 'Alumno no encontrado.', 'exito': False})
    except Exception as ex:
        return jsonify({'mensaje': 'Error {0}'.format(ex), 'exito': False})

@app.route("/alumnos/<mat>", methods=['DELETE'])
def eliminar_alumno(mat):
    try:
        alumno = leer_alumno_bd(mat)
        if alumno != None:
            cursor = conexion.connection.cursor()
            sql = "DELETE FROM alumnos WHERE matricula = '{0}'".format(mat)
            cursor.execute(sql)
            conexion.connection.commit()
            return jsonify({'mensaje': 'Alumno eliminado.', 'exito': True})
        else:
            return jsonify({'mensaje': 'Alumno no encontrado.', 'exito': False})
    except Exception as ex:
        return jsonify({'mensaje': 'Error {0}'.format(ex), 'exito': False})

@app.route("/hola")
def hola():
    return "<h3>saludo desde Hola<h3/>"

@app.route("/user/<string:user>")
def user(user):
    return "Hola " + user

@app.route("/numero/<int:n>")
def numero(n):
    return "Numero: {}".format(n)

@app.route("/user/<int:id>/<string:username>")
def username(id, username):
    return "ID: {} nombre: {}".format(id, username)

@app.route("/suma/<float:n1>/<float:n2>")
def func(n1, n2):
    return "lasuma es: {}".format(n1 + n2)

def pagina_no_encontrada(error):
    return "<h1>Pagina no encontrada</h1>", 404

if __name__ == "__main__":
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(host='0.0.0.0', port=5000, debug=True)