import hmac
import os
import sqlite3
from datetime import timedelta
from functools import wraps

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from werkzeug.security import check_password_hash

# Configuración por variables de entorno (no hay credenciales en el código):
#   SIO_SECRET_KEY           clave para firmar la cookie de sesión
#   SIO_ADMIN_USER           usuario de la intranet
#   SIO_ADMIN_PASSWORD_HASH  hash de la contraseña, generado con:
#       python -c "from werkzeug.security import generate_password_hash as g; print(g('LA_CONTRASEÑA'))"
#   SIO_CORS_ORIGINS         orígenes permitidos separados por comas (solo desarrollo)
#   FLASK_DEBUG=1            activa el modo debug (nunca en el servidor)
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SIO_SECRET_KEY'),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
)
ADMIN_USER = os.environ.get('SIO_ADMIN_USER')
ADMIN_PASSWORD_HASH = os.environ.get('SIO_ADMIN_PASSWORD_HASH')

# En producción la web y la API van por el mismo dominio y no hace falta CORS
origenes_cors = os.environ.get('SIO_CORS_ORIGINS', 'http://localhost:5173')
CORS(app, origins=[o.strip() for o in origenes_cors.split(',') if o.strip()], supports_credentials=True)


def login_configurado():
    return bool(app.config['SECRET_KEY'] and ADMIN_USER and ADMIN_PASSWORD_HASH)


def requiere_login(vista):
    @wraps(vista)
    def envoltorio(*args, **kwargs):
        if not session.get('autenticado'):
            return jsonify({"error": "No autorizado"}), 401
        return vista(*args, **kwargs)
    return envoltorio


# =======================================================
# SESIÓN DE LA INTRANET
# =======================================================

@app.route('/api/login', methods=['POST'])
def login():
    if not login_configurado():
        return jsonify({"error": "Login no configurado en el servidor"}), 503
    datos = request.get_json(silent=True) or {}
    usuario = datos.get('usuario', '')
    password = datos.get('password', '')
    if hmac.compare_digest(usuario, ADMIN_USER) and check_password_hash(ADMIN_PASSWORD_HASH, password):
        session.clear()
        session['autenticado'] = True
        session.permanent = bool(datos.get('recordar'))
        return jsonify({"autenticado": True})
    return jsonify({"error": "Usuario o contraseña incorrectos"}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"autenticado": False})


@app.route('/api/sesion', methods=['GET'])
def estado_sesion():
    return jsonify({"autenticado": bool(session.get('autenticado'))})


# Función para conectarnos a la base de datos
def conectar_bd():
    conexion = sqlite3.connect('sio_inventario.db')
    conexion.row_factory = sqlite3.Row 
    return conexion

# Ruta principal: GET para leer, POST para escribir
@app.route('/api/instrumentos', methods=['GET', 'POST'])
def gestionar_instrumentos():
    
    # Si la web pide LEER los instrumentos
    if request.method == 'GET':
        try:
            conexion = conectar_bd()
            instrumentos = conexion.execute('SELECT * FROM instrumentos').fetchall()
            conexion.close()
            lista_instrumentos = [dict(fila) for fila in instrumentos]
            return jsonify(lista_instrumentos)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Si la web pide GUARDAR un instrumento nuevo
    if request.method == 'POST':
        if not session.get('autenticado'):
            return jsonify({"error": "No autorizado"}), 401
        try:
            nuevo_equipo = request.json
            
            conexion = conectar_bd()
            cursor = conexion.cursor()
            
            cursor.execute('''
                INSERT INTO instrumentos 
                (categoria, subcategoria, nombre, marca, estado, ultima_calibracion, descripcion, parametros_tecnicos, numero_serie)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nuevo_equipo.get('categoria', 'Física'),
                nuevo_equipo.get('subcategoria', 'General'),
                nuevo_equipo.get('nombre', 'Sense Nom'),
                nuevo_equipo.get('marca', ''),
                nuevo_equipo.get('estado', 'Disponible'),
                nuevo_equipo.get('ultima_calibracion', ''),
                nuevo_equipo.get('descripcion', ''),
                nuevo_equipo.get('parametros_tecnicos', ''),
                nuevo_equipo.get('numero_serie', '')
            ))
            
            conexion.commit()
            conexion.close()
            
            return jsonify({"mensaje": "Equip desat correctament al SIO!"}), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# Ruta para modificar: PUT para editar, DELETE para borrar
@app.route('/api/instrumentos/<int:id>', methods=['PUT', 'DELETE'])
@requiere_login
def modificar_instrumento(id):

    # Si la web pide ELIMINAR
    if request.method == 'DELETE':
        conn = sqlite3.connect('sio_inventario.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM instrumentos WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return '', 204

    # Si la web pide ACTUALIZAR / EDITAR
    if request.method == 'PUT':
        try:
            datos = request.json
            conn = sqlite3.connect('sio_inventario.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE instrumentos 
                SET nombre = ?, marca = ?, categoria = ?, subcategoria = ?, 
                    ultima_calibracion = ?, descripcion = ?, parametros_tecnicos = ?, numero_serie = ?
                WHERE id = ?
            ''', (
                datos.get('nombre'), 
                datos.get('marca'), 
                datos.get('categoria'), 
                datos.get('subcategoria'), 
                datos.get('ultima_calibracion'), 
                datos.get('descripcion'), 
                datos.get('parametros_tecnicos'),
                datos.get('numero_serie'), 
                id
            ))
            
            conn.commit()
            conn.close()
            return jsonify({'mensaje': 'Instrumento actualizado correctamente'}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
# =======================================================
# RUTAS PARA PROYECTOS (Añadido con las nuevas descripciones y PIT)
# =======================================================

@app.route('/api/proyectos', methods=['GET', 'POST'])
def gestionar_proyectos():
    
    # LEER proyectos
    if request.method == 'GET':
        try:
            conexion = conectar_bd()
            proyectos = conexion.execute('SELECT * FROM proyectos').fetchall()
            conexion.close()
            return jsonify([dict(fila) for fila in proyectos])
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # GUARDAR nuevo proyecto
    if request.method == 'POST':
        if not session.get('autenticado'):
            return jsonify({"error": "No autorizado"}), 401
        try:
            datos = request.json
            conexion = conectar_bd()
            cursor = conexion.cursor()
            
            # AÑADIDO: pit en el INSERT
            cursor.execute('''
                INSERT INTO proyectos 
                (titulo, categoria, estado, descripcion_corta, descripcion_ampliada, investigador_principal, pit)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datos.get('titulo', ''),
                datos.get('categoria', ''),
                datos.get('estado', ''),
                datos.get('descripcion_corta', ''),
                datos.get('descripcion_ampliada', ''),
                datos.get('investigador_principal', ''),
                datos.get('pit', '') # <-- Aquí recogemos el PIT
            ))
            
            conexion.commit()
            conexion.close()
            return jsonify({"mensaje": "Projecte registrat correctament"}), 201
            
        except Exception as e:
            print("Error en POST:", e)
            return jsonify({"error": str(e)}), 500


@app.route('/api/proyectos/<int:id>', methods=['PUT', 'DELETE'])
@requiere_login
def modificar_proyecto(id):

    # ELIMINAR proyecto
    if request.method == 'DELETE':
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM proyectos WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return '', 204

    # EDITAR proyecto
    if request.method == 'PUT':
        try:
            datos = request.json
            conn = conectar_bd()
            cursor = conn.cursor()
            
            # AÑADIDO: pit = ? en el UPDATE
            cursor.execute('''
                UPDATE proyectos 
                SET titulo = ?, categoria = ?, estado = ?, 
                    descripcion_corta = ?, descripcion_ampliada = ?, investigador_principal = ?, pit = ?
                WHERE id = ?
            ''', (
                datos.get('titulo'), 
                datos.get('categoria'), 
                datos.get('estado'), 
                datos.get('descripcion_corta'), 
                datos.get('descripcion_ampliada'), 
                datos.get('investigador_principal'),
                datos.get('pit'), # <-- Aquí recogemos el PIT
                id
            ))
            
            conn.commit()
            conn.close()
            return jsonify({'mensaje': 'Projecte actualitzat correctament'}), 200
        except Exception as e:
            print("Error en PUT:", e)
            return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    if not login_configurado():
        print("⚠️  Faltan SIO_SECRET_KEY, SIO_ADMIN_USER o SIO_ADMIN_PASSWORD_HASH: la intranet no podrá iniciar sesión")
    print("🚀 Arrancando el motor del SIO en http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=os.environ.get('FLASK_DEBUG') == '1')