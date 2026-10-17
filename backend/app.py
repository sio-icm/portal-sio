import hmac
import os
import re
import smtplib
import sqlite3
import time
from collections import defaultdict, deque
from datetime import timedelta
from email.message import EmailMessage
from functools import wraps

from flask import Flask, jsonify, request, session
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash

# Configuración por variables de entorno (no hay credenciales en el código):
#   SIO_SECRET_KEY           clave para firmar la cookie de sesión
#   SIO_ADMIN_USER           usuario de la intranet
#   SIO_ADMIN_PASSWORD_HASH  hash de la contraseña, generado con:
#       python -c "from werkzeug.security import generate_password_hash as g; print(g('LA_CONTRASEÑA'))"
#   SIO_SMTP_HOST            servidor de correo para el formulario de contacto
#   SIO_SMTP_PORT            puerto (por defecto 25)
#   SIO_SMTP_STARTTLS=1      usar STARTTLS
#   SIO_SMTP_USER / SIO_SMTP_PASSWORD   solo si el servidor pide autenticación
#   SIO_SMTP_FROM            remitente de los correos (por defecto el destinatario)
#   SIO_CONTACTO_DESTINO     destinatario de las consultas (por defecto sio@icm.csic.es)
#   SIO_COOKIE_SEGURA=1      la cookie de sesión solo viaja por HTTPS (activar con el certificado)
#   SIO_DB_PATH              ruta de la base de datos (por defecto sio_inventario.db junto a este archivo)
#   FLASK_DEBUG=1            activa el modo debug (nunca en el servidor)
app = Flask(__name__)
# Detrás de Nginx: la IP real del usuario llega en X-Forwarded-For
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
app.config.update(
    SECRET_KEY=os.environ.get('SIO_SECRET_KEY'),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.environ.get('SIO_COOKIE_SEGURA') == '1',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
)
ADMIN_USER = os.environ.get('SIO_ADMIN_USER')
ADMIN_PASSWORD_HASH = os.environ.get('SIO_ADMIN_PASSWORD_HASH')

# Sin CORS: la web y la API van por el mismo dominio (Nginx en producción,
# proxy de Vite en desarrollo)


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


# =======================================================
# FORMULARIO DE CONTACTO
# =======================================================

CONTACTO_DESTINO = os.environ.get('SIO_CONTACTO_DESTINO', 'sio@icm.csic.es')
PATRON_EMAIL = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
MAX_ENVIOS_POR_HORA = 5
envios_por_ip = defaultdict(deque)


def demasiados_envios(ip):
    ahora = time.time()
    envios = envios_por_ip[ip]
    while envios and ahora - envios[0] > 3600:
        envios.popleft()
    if len(envios) >= MAX_ENVIOS_POR_HORA:
        return True
    envios.append(ahora)
    return False


def enviar_correo(mensaje):
    host = os.environ['SIO_SMTP_HOST']
    puerto = int(os.environ.get('SIO_SMTP_PORT', '25'))
    with smtplib.SMTP(host, puerto, timeout=15) as smtp:
        if os.environ.get('SIO_SMTP_STARTTLS') == '1':
            smtp.starttls()
        if os.environ.get('SIO_SMTP_USER'):
            smtp.login(os.environ['SIO_SMTP_USER'], os.environ.get('SIO_SMTP_PASSWORD', ''))
        smtp.send_message(mensaje)


@app.route('/api/contacto', methods=['POST'])
def contacto():
    datos = request.get_json(silent=True) or {}

    # Campo trampa: los humanos no lo ven, los bots lo rellenan
    if datos.get('web'):
        return jsonify({"mensaje": "Consulta enviada"}), 200

    nombre = str(datos.get('nombre', '')).strip()
    email = str(datos.get('email', '')).strip()
    texto = str(datos.get('mensaje', '')).strip()

    if not nombre or not texto or not PATRON_EMAIL.match(email):
        return jsonify({"error": "Revisa el nombre, el email y el mensaje"}), 400
    if len(nombre) > 200 or len(email) > 254 or len(texto) > 5000 or '\n' in nombre or '\r' in nombre:
        return jsonify({"error": "Algún campo es demasiado largo"}), 400

    if not os.environ.get('SIO_SMTP_HOST'):
        return jsonify({"error": "Envío no configurado en el servidor"}), 503
    if demasiados_envios(request.remote_addr):
        return jsonify({"error": "Demasiadas consultas. Inténtalo más tarde"}), 429

    mensaje = EmailMessage()
    mensaje['Subject'] = f'Consulta desde la web del SIO: {nombre}'
    mensaje['From'] = os.environ.get('SIO_SMTP_FROM', CONTACTO_DESTINO)
    mensaje['To'] = CONTACTO_DESTINO
    mensaje['Reply-To'] = email
    mensaje.set_content(f'Nombre: {nombre}\nEmail: {email}\n\n{texto}\n')

    try:
        enviar_correo(mensaje)
    except Exception as e:
        print("Error enviando consulta:", e)
        return jsonify({"error": "No se ha podido enviar la consulta"}), 502
    return jsonify({"mensaje": "Consulta enviada"}), 200


# La base de datos se busca junto a este archivo, no en la carpeta desde la que se arranca
DB_PATH = os.environ.get('SIO_DB_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sio_inventario.db'))


# Función para conectarnos a la base de datos
def conectar_bd():
    conexion = sqlite3.connect(DB_PATH)
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
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM instrumentos WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return '', 204

    # Si la web pide ACTUALIZAR / EDITAR
    if request.method == 'PUT':
        try:
            datos = request.json
            conn = conectar_bd()
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