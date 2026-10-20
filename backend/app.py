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
from werkzeug.security import check_password_hash, generate_password_hash

# Configuración por variables de entorno (no hay credenciales en el código):
#   SIO_SECRET_KEY           clave para firmar la cookie de sesión
#   SIO_ADMIN_USER           usuario administrador de la intranet (los demás usuarios
#                            se crean desde la intranet y se guardan en la base de datos)
#   SIO_ADMIN_PASSWORD_HASH  hash de su contraseña, generado con:
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
    return bool(app.config['SECRET_KEY'])


def requiere_login(vista):
    @wraps(vista)
    def envoltorio(*args, **kwargs):
        if not session.get('autenticado'):
            return jsonify({"error": "No autorizado"}), 401
        return vista(*args, **kwargs)
    return envoltorio


def requiere_admin(vista):
    @wraps(vista)
    def envoltorio(*args, **kwargs):
        if not session.get('autenticado'):
            return jsonify({"error": "No autorizado"}), 401
        if not session.get('es_admin'):
            return jsonify({"error": "Solo para administradores"}), 403
        return vista(*args, **kwargs)
    return envoltorio


# Límite de intentos de login fallidos por IP (contra quien prueba contraseñas)
MAX_FALLOS_LOGIN = 10
VENTANA_FALLOS_LOGIN = 15 * 60
fallos_login = defaultdict(deque)


def login_bloqueado(ip):
    ahora = time.time()
    fallos = fallos_login[ip]
    while fallos and ahora - fallos[0] > VENTANA_FALLOS_LOGIN:
        fallos.popleft()
    return len(fallos) >= MAX_FALLOS_LOGIN


def iniciar_sesion(usuario_id, nombre, es_admin, recordar):
    session.clear()
    session['autenticado'] = True
    session['usuario_id'] = usuario_id
    session['nombre'] = nombre
    session['es_admin'] = bool(es_admin)
    session.permanent = bool(recordar)


# =======================================================
# SESIÓN DE LA INTRANET
# =======================================================

@app.route('/api/login', methods=['POST'])
def login():
    if not login_configurado():
        return jsonify({"error": "Login no configurado en el servidor"}), 503
    ip = request.remote_addr
    if login_bloqueado(ip):
        return jsonify({"error": "Demasiados intentos. Espera unos minutos"}), 429
    datos = request.get_json(silent=True) or {}
    usuario = str(datos.get('usuario', '')).strip()
    password = str(datos.get('password', ''))
    recordar = datos.get('recordar')

    # 1) Administrador definido en el servidor (backend.env)
    if ADMIN_USER and ADMIN_PASSWORD_HASH and hmac.compare_digest(usuario, ADMIN_USER) \
            and check_password_hash(ADMIN_PASSWORD_HASH, password):
        iniciar_sesion(None, ADMIN_USER, True, recordar)
        return jsonify(datos_sesion())

    # 2) Usuarios personales creados desde la intranet
    conexion = conectar_bd()
    fila = conexion.execute('SELECT * FROM usuarios WHERE usuario = ? AND activo = 1', (usuario,)).fetchone()
    conexion.close()
    if fila and check_password_hash(fila['password_hash'], password):
        iniciar_sesion(fila['id'], fila['nombre'], fila['es_admin'], recordar)
        return jsonify(datos_sesion())

    fallos_login[ip].append(time.time())
    return jsonify({"error": "Usuario o contraseña incorrectos"}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"autenticado": False})


def datos_sesion():
    if not session.get('autenticado'):
        return {"autenticado": False}
    return {
        "autenticado": True,
        "usuario_id": session.get('usuario_id'),
        "nombre": session.get('nombre') or ADMIN_USER,
        "es_admin": bool(session.get('es_admin', True)),
    }


@app.route('/api/sesion', methods=['GET'])
def estado_sesion():
    return jsonify(datos_sesion())


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


# =======================================================
# USUARIOS Y DIARIO DE ACTIVIDAD
# =======================================================

TIPOS_NOTA = ['campanya', 'desenvolupament', 'manteniment', 'calibratge',
              'divulgacio', 'formacio', 'gestio', 'altres']
VISIBILIDADES = ['interna', 'publica']
PATRON_FECHA = re.compile(r'^\d{4}-\d{2}-\d{2}$')
PATRON_USUARIO = re.compile(r'^[a-z0-9._-]{3,30}$')


def crear_tablas():
    """Crea las tablas nuevas si no existen (la base de datos ya está en uso)."""
    conexion = conectar_bd()
    conexion.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            es_admin INTEGER NOT NULL DEFAULT 0,
            activo INTEGER NOT NULL DEFAULT 1,
            creado TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            usuario_id INTEGER REFERENCES usuarios(id),
            autor TEXT NOT NULL,
            proyecto_id INTEGER REFERENCES proyectos(id),
            tipo TEXT NOT NULL DEFAULT 'altres',
            titulo TEXT NOT NULL,
            texto TEXT NOT NULL DEFAULT '',
            visibilidad TEXT NOT NULL DEFAULT 'interna',
            creado TEXT NOT NULL DEFAULT (datetime('now')),
            actualizado TEXT
        );
        CREATE INDEX IF NOT EXISTS notas_fecha ON notas(fecha);
    """)
    conexion.commit()
    conexion.close()


crear_tablas()


def validar_nota(datos):
    """Devuelve (valores, error). proyecto_id puede ser None (nota sin proyecto)."""
    fecha = str(datos.get('fecha', '')).strip()
    titulo = str(datos.get('titulo', '')).strip()
    texto = str(datos.get('texto', '') or '')
    tipo = datos.get('tipo') or 'altres'
    visibilidad = datos.get('visibilidad') or 'interna'
    proyecto_id = datos.get('proyecto_id')

    if not PATRON_FECHA.match(fecha):
        return None, "Fecha no válida (AAAA-MM-DD)"
    if not titulo or len(titulo) > 200:
        return None, "El título es obligatorio (máximo 200 caracteres)"
    if len(texto) > 100000:
        return None, "El texto es demasiado largo"
    if tipo not in TIPOS_NOTA:
        return None, "Tipo no válido"
    if visibilidad not in VISIBILIDADES:
        return None, "Visibilidad no válida"
    if proyecto_id in ('', None):
        proyecto_id = None
    else:
        try:
            proyecto_id = int(proyecto_id)
        except (TypeError, ValueError):
            return None, "Proyecto no válido"
        conexion = conectar_bd()
        existe = conexion.execute('SELECT 1 FROM proyectos WHERE id = ?', (proyecto_id,)).fetchone()
        conexion.close()
        if not existe:
            return None, "El proyecto no existe"
    return (fecha, titulo, texto, tipo, visibilidad, proyecto_id), None


def puede_editar(nota):
    if session.get('es_admin'):
        return True
    return nota['usuario_id'] is not None and nota['usuario_id'] == session.get('usuario_id')


@app.route('/api/notas', methods=['GET', 'POST'])
@requiere_login
def gestionar_notas():
    if request.method == 'GET':
        condiciones, valores = [], []
        if request.args.get('desde'):
            condiciones.append('n.fecha >= ?')
            valores.append(request.args['desde'])
        if request.args.get('hasta'):
            condiciones.append('n.fecha <= ?')
            valores.append(request.args['hasta'])
        proyecto = request.args.get('proyecto')
        if proyecto == 'ninguno':
            condiciones.append('n.proyecto_id IS NULL')
        elif proyecto:
            condiciones.append('n.proyecto_id = ?')
            valores.append(proyecto)
        if request.args.get('tipo'):
            condiciones.append('n.tipo = ?')
            valores.append(request.args['tipo'])
        if request.args.get('autor'):
            condiciones.append('n.autor = ?')
            valores.append(request.args['autor'])
        donde = ('WHERE ' + ' AND '.join(condiciones)) if condiciones else ''
        conexion = conectar_bd()
        filas = conexion.execute(
            'SELECT n.*, p.titulo AS proyecto_titulo '
            'FROM notas n LEFT JOIN proyectos p ON p.id = n.proyecto_id '
            f'{donde} ORDER BY n.fecha DESC, n.id DESC', valores).fetchall()
        conexion.close()
        return jsonify([dict(f) for f in filas])

    valores, error = validar_nota(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400
    conexion = conectar_bd()
    cursor = conexion.execute(
        'INSERT INTO notas (fecha, titulo, texto, tipo, visibilidad, proyecto_id, usuario_id, autor) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        valores + (session.get('usuario_id'), session.get('nombre') or ADMIN_USER))
    conexion.commit()
    nuevo_id = cursor.lastrowid
    conexion.close()
    return jsonify({"id": nuevo_id}), 201


@app.route('/api/notas/<int:id>', methods=['PUT', 'DELETE'])
@requiere_login
def modificar_nota(id):
    conexion = conectar_bd()
    nota = conexion.execute('SELECT * FROM notas WHERE id = ?', (id,)).fetchone()
    if not nota:
        conexion.close()
        return jsonify({"error": "La nota no existe"}), 404
    if not puede_editar(nota):
        conexion.close()
        return jsonify({"error": "Solo puede modificarla quien la escribió o un administrador"}), 403

    if request.method == 'DELETE':
        conexion.execute('DELETE FROM notas WHERE id = ?', (id,))
        conexion.commit()
        conexion.close()
        return '', 204

    valores, error = validar_nota(request.get_json(silent=True) or {})
    if error:
        conexion.close()
        return jsonify({"error": error}), 400
    conexion.execute(
        'UPDATE notas SET fecha = ?, titulo = ?, texto = ?, tipo = ?, visibilidad = ?, proyecto_id = ?, '
        "actualizado = datetime('now') WHERE id = ?", valores + (id,))
    conexion.commit()
    conexion.close()
    return jsonify({"id": id})


@app.route('/api/usuarios', methods=['GET', 'POST'])
@requiere_admin
def gestionar_usuarios():
    conexion = conectar_bd()
    if request.method == 'GET':
        filas = conexion.execute(
            'SELECT id, usuario, nombre, es_admin, activo, creado FROM usuarios ORDER BY nombre').fetchall()
        conexion.close()
        return jsonify([dict(f) for f in filas])

    datos = request.get_json(silent=True) or {}
    usuario = str(datos.get('usuario', '')).strip().lower()
    nombre = str(datos.get('nombre', '')).strip()
    password = str(datos.get('password', ''))
    error = None
    if not PATRON_USUARIO.match(usuario):
        error = "Usuario: de 3 a 30 letras minúsculas, números, punto, guion o guion bajo"
    elif usuario == (ADMIN_USER or '').lower():
        error = "Ese nombre de usuario está reservado"
    elif not nombre or len(nombre) > 100:
        error = "El nombre es obligatorio"
    elif len(password) < 8:
        error = "La contraseña debe tener al menos 8 caracteres"
    if error:
        conexion.close()
        return jsonify({"error": error}), 400
    try:
        conexion.execute(
            'INSERT INTO usuarios (usuario, nombre, password_hash, es_admin) VALUES (?, ?, ?, ?)',
            (usuario, nombre, generate_password_hash(password), 1 if datos.get('es_admin') else 0))
        conexion.commit()
    except sqlite3.IntegrityError:
        conexion.close()
        return jsonify({"error": "Ese usuario ya existe"}), 400
    conexion.close()
    return jsonify({"usuario": usuario}), 201


@app.route('/api/usuarios/<int:id>', methods=['PUT'])
@requiere_admin
def modificar_usuario(id):
    datos = request.get_json(silent=True) or {}
    cambios, valores = [], []
    if 'nombre' in datos:
        nombre = str(datos['nombre']).strip()
        if not nombre:
            return jsonify({"error": "El nombre es obligatorio"}), 400
        cambios.append('nombre = ?')
        valores.append(nombre)
    if 'es_admin' in datos:
        cambios.append('es_admin = ?')
        valores.append(1 if datos['es_admin'] else 0)
    if 'activo' in datos:
        cambios.append('activo = ?')
        valores.append(1 if datos['activo'] else 0)
    if datos.get('password'):
        if len(str(datos['password'])) < 8:
            return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400
        cambios.append('password_hash = ?')
        valores.append(generate_password_hash(str(datos['password'])))
    conexion = conectar_bd()
    if not conexion.execute('SELECT 1 FROM usuarios WHERE id = ?', (id,)).fetchone():
        conexion.close()
        return jsonify({"error": "El usuario no existe"}), 404
    if cambios:
        conexion.execute(f'UPDATE usuarios SET {", ".join(cambios)} WHERE id = ?', valores + [id])
        conexion.commit()
    conexion.close()
    return jsonify({"id": id})


@app.route('/api/mi-contrasena', methods=['POST'])
@requiere_login
def cambiar_mi_contrasena():
    if session.get('usuario_id') is None:
        return jsonify({"error": "La contraseña del administrador del servidor se cambia en backend.env"}), 400
    datos = request.get_json(silent=True) or {}
    actual, nueva = str(datos.get('actual', '')), str(datos.get('nueva', ''))
    if len(nueva) < 8:
        return jsonify({"error": "La contraseña nueva debe tener al menos 8 caracteres"}), 400
    conexion = conectar_bd()
    fila = conexion.execute('SELECT password_hash FROM usuarios WHERE id = ?', (session['usuario_id'],)).fetchone()
    if not fila or not check_password_hash(fila['password_hash'], actual):
        conexion.close()
        return jsonify({"error": "La contraseña actual no es correcta"}), 400
    conexion.execute('UPDATE usuarios SET password_hash = ? WHERE id = ?',
                     (generate_password_hash(nueva), session['usuario_id']))
    conexion.commit()
    conexion.close()
    return jsonify({"cambiada": True})


if __name__ == '__main__':
    if not login_configurado():
        print("⚠️  Faltan SIO_SECRET_KEY, SIO_ADMIN_USER o SIO_ADMIN_PASSWORD_HASH: la intranet no podrá iniciar sesión")
    print("🚀 Arrancando el motor del SIO en http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=os.environ.get('FLASK_DEBUG') == '1')