import hmac
import json as json_lib
import os
import re
import smtplib
import sqlite3
import time
import uuid
from collections import defaultdict, deque
from datetime import date, timedelta
from email.message import EmailMessage
from functools import wraps

from flask import Flask, jsonify, request, send_from_directory, session
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from PIL import Image, ImageOps, UnidentifiedImageError
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
#   SIO_FOTOS_DIR            carpeta de las fotos del diario (por defecto fotos/ junto a la base de datos)
#   SIO_URL_PUBLICA          adreça de la web als enllaços dels correus (per defecte https://sio.icm.csic.es)
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
    MAX_CONTENT_LENGTH=40 * 1024 * 1024,  # subida de fotos del diario
)
ADMIN_USER = os.environ.get('SIO_ADMIN_USER')
ADMIN_PASSWORD_HASH = os.environ.get('SIO_ADMIN_PASSWORD_HASH')

# Sin CORS: la web y la API van por el mismo dominio (Nginx en producción,
# proxy de Vite en desarrollo)


def login_configurado():
    return bool(app.config['SECRET_KEY'])


# Mientras un usuario tenga que cambiar la contraseña (primer acceso o contraseña
# puesta por un administrador), solo puede usar estas rutas
RUTAS_SIN_CAMBIO_CONTRASENA = {'cambiar_mi_contrasena'}


def debe_cambiar_bloquea(vista):
    return session.get('debe_cambiar') and vista.__name__ not in RUTAS_SIN_CAMBIO_CONTRASENA


def requiere_login(vista):
    @wraps(vista)
    def envoltorio(*args, **kwargs):
        if not session.get('autenticado'):
            return jsonify({"error": "No autorizado"}), 401
        if debe_cambiar_bloquea(vista):
            return jsonify({"error": "Tienes que cambiar la contraseña", "debe_cambiar": True}), 403
        return vista(*args, **kwargs)
    return envoltorio


def requiere_admin(vista):
    @wraps(vista)
    def envoltorio(*args, **kwargs):
        if not session.get('autenticado'):
            return jsonify({"error": "No autorizado"}), 401
        if debe_cambiar_bloquea(vista):
            return jsonify({"error": "Tienes que cambiar la contraseña", "debe_cambiar": True}), 403
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


def iniciar_sesion(usuario_id, nombre, es_admin, recordar, debe_cambiar=False):
    session.clear()
    session['autenticado'] = True
    session['usuario_id'] = usuario_id
    session['nombre'] = nombre
    session['es_admin'] = bool(es_admin)
    session['debe_cambiar'] = bool(debe_cambiar)
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
        iniciar_sesion(fila['id'], fila['nombre'], fila['es_admin'], recordar, fila['debe_cambiar'])
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
        "debe_cambiar": bool(session.get('debe_cambiar')),
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


# =======================================================
# SOLICITUDES DE SERVICIOS (Pelagia, tanque, instrumentos...)
# =======================================================
# La web prepara el asunto y el texto en el idioma del usuario y el servidor los
# envía a sio@icm.csic.es con Reply-To del solicitante: así no hace falta abrir
# el programa de correo de quien la pide.

TIPOS_SOLICITUD = {'pelagia', 'tanque', 'instrumento', 'salinidad', 'fondeo', 'prototipado', 'idi'}
EXTENSIONES_ADJUNTO = {
    '.pdf': ('application', 'pdf'),
    '.doc': ('application', 'msword'),
    '.docx': ('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document'),
    '.odt': ('application', 'vnd.oasis.opendocument.text'),
}
MAX_ADJUNTO = 10 * 1024 * 1024
MAX_SOLICITUDES_POR_HORA = 10
solicitudes_por_ip = defaultdict(deque)


def demasiadas_solicitudes(ip):
    ahora = time.time()
    envios = solicitudes_por_ip[ip]
    while envios and ahora - envios[0] > 3600:
        envios.popleft()
    if len(envios) >= MAX_SOLICITUDES_POR_HORA:
        return True
    envios.append(ahora)
    return False


@app.route('/api/solicitud', methods=['POST'])
def solicitud():
    datos = request.form

    # Campo trampa: los humanos no lo ven, los bots lo rellenan
    if datos.get('web'):
        return jsonify({"mensaje": "Solicitud enviada"}), 200

    tipo = datos.get('tipo', '').strip()
    nombre = datos.get('nombre', '').strip()
    email = datos.get('email', '').strip()
    asunto = datos.get('asunto', '').strip()
    cuerpo = datos.get('cuerpo', '').strip()

    if tipo not in TIPOS_SOLICITUD or not nombre or not asunto or not cuerpo or not PATRON_EMAIL.match(email):
        return jsonify({"error": "Revisa el nombre, el email y los datos de la solicitud"}), 400
    if (len(nombre) > 200 or len(email) > 254 or len(asunto) > 250 or len(cuerpo) > 10000
            or any(c in campo for campo in (nombre, email, asunto) for c in '\r\n')):
        return jsonify({"error": "Algún campo es demasiado largo"}), 400

    adjunto = request.files.get('adjunto')
    contenido_adjunto = None
    if adjunto and adjunto.filename:
        extension = os.path.splitext(adjunto.filename)[1].lower()
        if extension not in EXTENSIONES_ADJUNTO:
            return jsonify({"error": "El archivo adjunto debe ser PDF o Word"}), 415
        contenido_adjunto = adjunto.read(MAX_ADJUNTO + 1)
        if len(contenido_adjunto) > MAX_ADJUNTO:
            return jsonify({"error": "El archivo adjunto ocupa más de 10 MB"}), 413
    elif tipo == 'pelagia':
        return jsonify({"error": "Falta el Plan de Campaña"}), 400

    if not os.environ.get('SIO_SMTP_HOST'):
        return jsonify({"error": "Envío no configurado en el servidor"}), 503
    if demasiadas_solicitudes(request.remote_addr):
        return jsonify({"error": "Demasiadas solicitudes. Inténtalo más tarde"}), 429

    mensaje = EmailMessage()
    mensaje['Subject'] = f'[Web SIO] {asunto}'
    mensaje['From'] = os.environ.get('SIO_SMTP_FROM', CONTACTO_DESTINO)
    mensaje['To'] = CONTACTO_DESTINO
    mensaje['Reply-To'] = email
    mensaje.set_content(
        f'Solicitud enviada desde la web del SIO.\n'
        f'Nombre: {nombre}\nEmail: {email}\n'
        f'(Para contestar, responde a este correo: va a {email}.)\n\n'
        f'----------------------------------------\n\n{cuerpo}\n')
    if contenido_adjunto is not None:
        tipo_mime, subtipo = EXTENSIONES_ADJUNTO[os.path.splitext(adjunto.filename)[1].lower()]
        nombre_archivo = os.path.basename(adjunto.filename.replace('\\', '/'))[:150] or 'adjunto'
        mensaje.add_attachment(contenido_adjunto, maintype=tipo_mime, subtype=subtipo, filename=nombre_archivo)

    try:
        enviar_correo(mensaje)
    except Exception as e:
        print("Error enviando solicitud:", e)
        return jsonify({"error": "No se ha podido enviar la solicitud"}), 502
    return jsonify({"mensaje": "Solicitud enviada"}), 200


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
            # Si avui està prestat o reservat al calendari d'equip, fins quan (sense noms)
            hoy = date.today().isoformat()
            prestados = {f['instrumento_id']: f['hasta'] for f in conexion.execute(
                "SELECT instrumento_id, MAX(fin) AS hasta FROM reservas WHERE recurso = 'instrument' "
                "AND inicio <= ? AND fin >= ? GROUP BY instrumento_id", (hoy, hoy))}
            conexion.close()
            lista_instrumentos = [dict(fila, prestado_hasta=prestados.get(fila['id'])) for fila in instrumentos]
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
# Temps dedicat a una nota: intervals d'hores (el mateix a src/utils/diario.js)
INTERVALOS_HORAS = {'0-1': (0, 1), '1-3': (1, 3), '3-5': (3, 5), '5-8': (5, 8), '8+': (8, 16)}
PATRON_FECHA = re.compile(r'^\d{4}-\d{2}-\d{2}$')
PATRON_USUARIO = re.compile(r'^[a-z0-9._-]{3,30}$')
FOTOS_DIR = os.environ.get('SIO_FOTOS_DIR', os.path.join(os.path.dirname(DB_PATH), 'fotos'))
MAX_FOTOS_POR_NOTA = 12
LADO_FOTO, LADO_MINIATURA = 1600, 480


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
        CREATE TABLE IF NOT EXISTS fotos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nota_id INTEGER NOT NULL REFERENCES notas(id),
            archivo TEXT NOT NULL,
            creado TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS fotos_nota ON fotos(nota_id);
    """)
    # Columnas añadidas después (fase 2): aprobación de las notas públicas
    columnas = [fila['name'] for fila in conexion.execute('PRAGMA table_info(notas)')]
    if 'publicada' not in columnas:
        conexion.execute('ALTER TABLE notas ADD COLUMN publicada INTEGER NOT NULL DEFAULT 0')
    if 'publicada_por' not in columnas:
        conexion.execute('ALTER TABLE notas ADD COLUMN publicada_por TEXT')
    # Temps dedicat (interval d'hores) i per a qui és la feina (p. ex. Comunicació)
    for columna in ('horas', 'para'):
        if columna not in columnas:
            try:
                conexion.execute(f'ALTER TABLE notas ADD COLUMN {columna} TEXT')
            except sqlite3.OperationalError:
                pass  # l'altre procés de gunicorn l'ha afegit alhora
    # Usuarios que tienen que cambiar la contraseña al entrar
    columnas = [fila['name'] for fila in conexion.execute('PRAGMA table_info(usuarios)')]
    if 'debe_cambiar' not in columnas:
        conexion.execute('ALTER TABLE usuarios ADD COLUMN debe_cambiar INTEGER NOT NULL DEFAULT 0')
    conexion.commit()
    conexion.close()
    os.makedirs(FOTOS_DIR, exist_ok=True)


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


def extras_nota(datos):
    """Temps dedicat i «per a» (opcionals). Retorna ((horas, para), error)."""
    horas = datos.get('horas') or None
    para = str(datos.get('para') or '').strip() or None
    if horas is not None and horas not in INTERVALOS_HORAS:
        return None, "Tiempo dedicado no válido"
    if para is not None and len(para) > 100:
        return None, "«Para» es demasiado largo (máximo 100 caracteres)"
    return (horas, para), None


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
        notas = con_fotos(conexion, [dict(f) for f in filas])
        conexion.close()
        return jsonify(notas)

    datos = request.get_json(silent=True) or {}
    valores, error = validar_nota(datos)
    if not error:
        extras, error = extras_nota(datos)
    if error:
        return jsonify({"error": error}), 400
    conexion = conectar_bd()
    cursor = conexion.execute(
        'INSERT INTO notas (fecha, titulo, texto, tipo, visibilidad, proyecto_id, horas, para, usuario_id, autor) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        valores + extras + (session.get('usuario_id'), session.get('nombre') or ADMIN_USER))
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
        for foto in conexion.execute('SELECT archivo FROM fotos WHERE nota_id = ?', (id,)).fetchall():
            borrar_archivos_foto(foto['archivo'])
        conexion.execute('DELETE FROM fotos WHERE nota_id = ?', (id,))
        conexion.execute('DELETE FROM notas WHERE id = ?', (id,))
        conexion.commit()
        conexion.close()
        return '', 204

    datos = request.get_json(silent=True) or {}
    valores, error = validar_nota(datos)
    if not error:
        extras, error = extras_nota(datos)
    if error:
        conexion.close()
        return jsonify({"error": error}), 400
    # Si la nota deja de ser pública, o la cambia alguien que no es administrador,
    # deja de estar publicada y tiene que volver a aprobarse
    publicada = nota['publicada'] and valores[4] == 'publica' and session.get('es_admin')
    conexion.execute(
        'UPDATE notas SET fecha = ?, titulo = ?, texto = ?, tipo = ?, visibilidad = ?, proyecto_id = ?, '
        "horas = ?, para = ?, publicada = ?, actualizado = datetime('now') WHERE id = ?",
        valores + extras + (1 if publicada else 0, id))
    conexion.commit()
    conexion.close()
    return jsonify({"id": id})


def con_fotos(conexion, notas):
    """Añade a cada nota la lista de ids de sus fotos."""
    if not notas:
        return notas
    ids = [n['id'] for n in notas]
    marcas = ','.join('?' * len(ids))
    por_nota = defaultdict(list)
    for f in conexion.execute(f'SELECT id, nota_id FROM fotos WHERE nota_id IN ({marcas}) ORDER BY id', ids):
        por_nota[f['nota_id']].append(f['id'])
    for n in notas:
        n['fotos'] = por_nota.get(n['id'], [])
    return notas


def borrar_archivos_foto(archivo):
    for nombre in (archivo, 'mini-' + archivo):
        try:
            os.remove(os.path.join(FOTOS_DIR, nombre))
        except FileNotFoundError:
            pass


def guardar_foto(fichero):
    """Reduce la foto, la gira según el EXIF y la guarda en WebP (y una miniatura). Devuelve el nombre."""
    try:
        imagen = Image.open(fichero.stream)
        imagen.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        return None
    imagen = ImageOps.exif_transpose(imagen)
    if imagen.mode not in ('RGB', 'RGBA'):
        imagen = imagen.convert('RGB')
    nombre = uuid.uuid4().hex + '.webp'
    grande = imagen.copy()
    grande.thumbnail((LADO_FOTO, LADO_FOTO))
    grande.save(os.path.join(FOTOS_DIR, nombre), 'WEBP', quality=80, method=4)
    imagen.thumbnail((LADO_MINIATURA, LADO_MINIATURA))
    imagen.save(os.path.join(FOTOS_DIR, 'mini-' + nombre), 'WEBP', quality=75, method=4)
    return nombre


@app.route('/api/notas/<int:id>/fotos', methods=['POST'])
@requiere_login
def subir_fotos(id):
    conexion = conectar_bd()
    nota = conexion.execute('SELECT * FROM notas WHERE id = ?', (id,)).fetchone()
    if not nota:
        conexion.close()
        return jsonify({"error": "La nota no existe"}), 404
    if not puede_editar(nota):
        conexion.close()
        return jsonify({"error": "Solo puede añadir fotos quien escribió la nota o un administrador"}), 403
    ficheros = request.files.getlist('fotos')
    ya = conexion.execute('SELECT COUNT(*) FROM fotos WHERE nota_id = ?', (id,)).fetchone()[0]
    if not ficheros:
        conexion.close()
        return jsonify({"error": "No se ha recibido ninguna foto"}), 400
    if ya + len(ficheros) > MAX_FOTOS_POR_NOTA:
        conexion.close()
        return jsonify({"error": f"Máximo {MAX_FOTOS_POR_NOTA} fotos por nota"}), 400
    rechazadas = []
    for fichero in ficheros:
        nombre = guardar_foto(fichero)
        if nombre:
            conexion.execute('INSERT INTO fotos (nota_id, archivo) VALUES (?, ?)', (id, nombre))
        else:
            rechazadas.append(fichero.filename)
    conexion.commit()
    conexion.close()
    return jsonify({"rechazadas": rechazadas}), 201


@app.route('/api/fotos/<int:id>', methods=['GET', 'DELETE'])
def foto(id):
    conexion = conectar_bd()
    fila = conexion.execute(
        'SELECT f.archivo, n.* FROM fotos f JOIN notas n ON n.id = f.nota_id WHERE f.id = ?', (id,)).fetchone()
    conexion.close()
    if not fila:
        return jsonify({"error": "No existe"}), 404
    archivo = fila['archivo']

    if request.method == 'DELETE':
        if not session.get('autenticado'):
            return jsonify({"error": "No autorizado"}), 401
        if not puede_editar(fila):
            return jsonify({"error": "No puedes borrar esta foto"}), 403
        conexion = conectar_bd()
        conexion.execute('DELETE FROM fotos WHERE id = ?', (id,))
        conexion.commit()
        conexion.close()
        borrar_archivos_foto(archivo)
        return '', 204

    # Las fotos de notas aprobadas para la web las ve cualquiera; el resto, solo el equipo
    es_publica = fila['visibilidad'] == 'publica' and fila['publicada']
    if not es_publica and not session.get('autenticado'):
        return jsonify({"error": "No existe"}), 404
    nombre = ('mini-' + archivo) if request.args.get('mini') else archivo
    respuesta = send_from_directory(FOTOS_DIR, nombre, mimetype='image/webp', max_age=3600)
    if not es_publica:
        respuesta.headers['Cache-Control'] = 'private, max-age=3600'
    return respuesta


@app.route('/api/notas/<int:id>/publicacion', methods=['PUT'])
@requiere_admin
def publicar_nota(id):
    publicar = bool((request.get_json(silent=True) or {}).get('publicada'))
    conexion = conectar_bd()
    nota = conexion.execute('SELECT visibilidad FROM notas WHERE id = ?', (id,)).fetchone()
    if not nota:
        conexion.close()
        return jsonify({"error": "La nota no existe"}), 404
    if publicar and nota['visibilidad'] != 'publica':
        conexion.close()
        return jsonify({"error": "Solo se pueden publicar las notas marcadas como públicas"}), 400
    conexion.execute('UPDATE notas SET publicada = ?, publicada_por = ? WHERE id = ?',
                     (1 if publicar else 0, session.get('nombre') if publicar else None, id))
    conexion.commit()
    conexion.close()
    return jsonify({"id": id, "publicada": publicar})


@app.route('/api/diario', methods=['GET'])
def diario_publico():
    """Notas aprobadas para la web (sin login): el diario de campaña público."""
    try:
        limite = min(int(request.args.get('limite', 200)), 200)
    except ValueError:
        limite = 200
    conexion = conectar_bd()
    filas = conexion.execute(
        'SELECT n.id, n.fecha, n.titulo, n.texto, n.tipo, n.autor, n.proyecto_id, p.titulo AS proyecto_titulo '
        'FROM notas n LEFT JOIN proyectos p ON p.id = n.proyecto_id '
        "WHERE n.visibilidad = 'publica' AND n.publicada = 1 "
        'ORDER BY n.fecha DESC, n.id DESC LIMIT ?', (limite,)).fetchall()
    notas = con_fotos(conexion, [dict(f) for f in filas])
    conexion.close()
    return jsonify(notas)


@app.route('/api/usuarios', methods=['GET', 'POST'])
@requiere_admin
def gestionar_usuarios():
    conexion = conectar_bd()
    if request.method == 'GET':
        filas = conexion.execute(
            'SELECT id, usuario, nombre, email, es_admin, activo, debe_cambiar, plantilla, creado FROM usuarios ORDER BY nombre').fetchall()
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
    email = None
    if not error:
        email, error = validar_email_usuario(conexion, datos.get('email'))
    if error:
        conexion.close()
        return jsonify({"error": error}), 400
    try:
        conexion.execute(
            'INSERT INTO usuarios (usuario, nombre, email, password_hash, es_admin, debe_cambiar) VALUES (?, ?, ?, ?, ?, 1)',
            (usuario, nombre, email, generate_password_hash(password), 1 if datos.get('es_admin') else 0))
        conexion.commit()
    except sqlite3.IntegrityError:
        conexion.close()
        return jsonify({"error": "Ese usuario ya existe"}), 400
    conexion.close()
    return jsonify({"usuario": usuario}), 201


@app.route('/api/usuarios/<int:id>', methods=['PUT', 'DELETE'])
@requiere_admin
def modificar_usuario(id):
    if request.method == 'DELETE':
        if id == session.get('usuario_id'):
            return jsonify({"error": "No puedes borrar tu propio usuario"}), 400
        conexion = conectar_bd()
        if not conexion.execute('SELECT 1 FROM usuarios WHERE id = ?', (id,)).fetchone():
            conexion.close()
            return jsonify({"error": "El usuario no existe"}), 404
        notas = conexion.execute('SELECT COUNT(*) FROM notas WHERE usuario_id = ?', (id,)).fetchone()[0]
        if notas:
            conexion.close()
            return jsonify({"error": f"Tiene {notas} notas en el diario: no se puede borrar sin perderlas. Desactívalo."}), 400
        conexion.execute('DELETE FROM usuarios WHERE id = ?', (id,))
        conexion.commit()
        conexion.close()
        return '', 204

    datos = request.get_json(silent=True) or {}
    cambios, valores = [], []
    nombre_nuevo = None
    if 'usuario' in datos:
        usuario = str(datos['usuario']).strip().lower()
        if not PATRON_USUARIO.match(usuario):
            return jsonify({"error": "Usuario: de 3 a 30 letras minúsculas, números, punto, guion o guion bajo"}), 400
        if usuario == (ADMIN_USER or '').lower():
            return jsonify({"error": "Ese nombre de usuario está reservado"}), 400
        cambios.append('usuario = ?')
        valores.append(usuario)
    if 'nombre' in datos:
        nombre = str(datos['nombre']).strip()
        if not nombre:
            return jsonify({"error": "El nombre es obligatorio"}), 400
        cambios.append('nombre = ?')
        valores.append(nombre)
        nombre_nuevo = nombre
    if 'es_admin' in datos:
        cambios.append('es_admin = ?')
        valores.append(1 if datos['es_admin'] else 0)
    if 'activo' in datos:
        cambios.append('activo = ?')
        valores.append(1 if datos['activo'] else 0)
    if 'plantilla' in datos:
        cambios.append('plantilla = ?')
        valores.append(1 if datos['plantilla'] else 0)
    if datos.get('password'):
        if len(str(datos['password'])) < 8:
            return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400
        cambios.append('password_hash = ?')
        valores.append(generate_password_hash(str(datos['password'])))
        cambios.append('debe_cambiar = 1')
    conexion = conectar_bd()
    if not conexion.execute('SELECT 1 FROM usuarios WHERE id = ?', (id,)).fetchone():
        conexion.close()
        return jsonify({"error": "El usuario no existe"}), 404
    if 'email' in datos:
        email, error = validar_email_usuario(conexion, datos['email'], id)
        if error:
            conexion.close()
            return jsonify({"error": error}), 400
        cambios.append('email = ?')
        valores.append(email)
    if cambios:
        try:
            conexion.execute(f'UPDATE usuarios SET {", ".join(cambios)} WHERE id = ?', valores + [id])
        except sqlite3.IntegrityError:
            conexion.close()
            return jsonify({"error": "Ese usuario ya existe"}), 400
        # El nombre del autor también se guarda en cada nota: se corrige en todas las suyas
        if nombre_nuevo:
            conexion.execute('UPDATE notas SET autor = ? WHERE usuario_id = ?', (nombre_nuevo, id))
        conexion.commit()
    conexion.close()
    if nombre_nuevo and id == session.get('usuario_id'):
        session['nombre'] = nombre_nuevo
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
    if nueva == actual:
        return jsonify({"error": "La contraseña nueva tiene que ser distinta de la actual"}), 400
    conexion = conectar_bd()
    fila = conexion.execute('SELECT password_hash FROM usuarios WHERE id = ?', (session['usuario_id'],)).fetchone()
    if not fila or not check_password_hash(fila['password_hash'], actual):
        conexion.close()
        return jsonify({"error": "La contraseña actual no es correcta"}), 400
    conexion.execute('UPDATE usuarios SET password_hash = ?, debe_cambiar = 0 WHERE id = ?',
                     (generate_password_hash(nueva), session['usuario_id']))
    conexion.commit()
    conexion.close()
    session['debe_cambiar'] = False
    return jsonify({"cambiada": True})


# ---------------------------------------------------------------------------
# Calendari d'equip: qui és al centre, reserves de recursos i avisos
# ---------------------------------------------------------------------------
# Tipus d'entrada del calendari. FUERA_DEL_CENTRO = la persona no és al centre
# (compta per a l'avís de falta de personal). AUSENCIAS_PATRON = el patró no pot
# sortir amb la Pelagia (una «campanya» pot ser la mateixa sortida, no avisa).
TIPOS_CALENDARIO = ['teletreball', 'campanya', 'vacances', 'baixa', 'formacio', 'reunio', 'altres']
FUERA_DEL_CENTRO = {'teletreball', 'campanya', 'vacances', 'baixa', 'formacio'}
AUSENCIAS_PATRON = {'teletreball', 'vacances', 'baixa', 'formacio'}
RECURSOS = ['pelagia', 'tanc', 'instrument']
AJUSTES_INICIALES = {'minim_presents': '3', 'patro_pelagia': 'brian'}
MAX_DIAS_CONSULTA = 400

# Festius de Barcelona (Catalunya + els dos locals). Es poden afegir i treure
# des de la intranet; aquests només es carreguen la primera vegada.
FESTIUS_INICIALES = [
    ('2026-01-01', 'Any Nou'), ('2026-01-06', 'Reis'), ('2026-04-03', 'Divendres Sant'),
    ('2026-04-06', 'Dilluns de Pasqua'), ('2026-05-01', 'Festa del Treball'),
    ('2026-05-25', 'Segona Pasqua (local Barcelona)'), ('2026-06-24', 'Sant Joan'),
    ('2026-08-15', "L'Assumpció"), ('2026-09-11', 'Diada Nacional de Catalunya'),
    ('2026-09-24', 'La Mercè (local Barcelona)'), ('2026-10-12', "Festa Nacional d'Espanya"),
    ('2026-11-01', 'Tots Sants'), ('2026-12-08', 'La Immaculada'), ('2026-12-25', 'Nadal'),
    ('2026-12-26', 'Sant Esteve'),
    ('2027-01-01', 'Any Nou'), ('2027-01-06', 'Reis'), ('2027-03-26', 'Divendres Sant'),
    ('2027-03-29', 'Dilluns de Pasqua'), ('2027-05-01', 'Festa del Treball'),
    ('2027-05-17', 'Segona Pasqua (local Barcelona, pendent de confirmar)'), ('2027-06-24', 'Sant Joan'),
    ('2027-08-15', "L'Assumpció"), ('2027-09-11', 'Diada Nacional de Catalunya'),
    ('2027-09-24', 'La Mercè (local Barcelona, pendent de confirmar)'),
    ('2027-10-12', "Festa Nacional d'Espanya"), ('2027-11-01', 'Tots Sants'),
    ('2027-12-08', 'La Immaculada'), ('2027-12-25', 'Nadal'), ('2027-12-26', 'Sant Esteve'),
]


def crear_tablas_calendario():
    conexion = conectar_bd()
    conexion.executescript("""
        CREATE TABLE IF NOT EXISTS calendario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER REFERENCES usuarios(id),  -- NULL = tot l'equip
            tipo TEXT NOT NULL,
            inicio TEXT NOT NULL,
            fin TEXT NOT NULL,
            nota TEXT NOT NULL DEFAULT '',
            creado_por INTEGER,
            creado TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS calendario_fechas ON calendario(inicio, fin);
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recurso TEXT NOT NULL,
            instrumento_id INTEGER REFERENCES instrumentos(id),
            inicio TEXT NOT NULL,
            fin TEXT NOT NULL,
            usuario_id INTEGER REFERENCES usuarios(id),
            para TEXT NOT NULL DEFAULT '',
            proposito TEXT NOT NULL DEFAULT '',
            creado_por INTEGER,
            creado TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS reservas_fechas ON reservas(inicio, fin);
        CREATE TABLE IF NOT EXISTS festius (
            fecha TEXT PRIMARY KEY,
            nombre TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ajustes (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        );
    """)
    columnas = [fila['name'] for fila in conexion.execute('PRAGMA table_info(usuarios)')]
    columnas_cal = [fila['name'] for fila in conexion.execute('PRAGMA table_info(calendario)')]
    if 'proyecto_id' not in columnas_cal:
        try:  # projecte de l'entrada (p. ex. la campanya de SALADET)
            conexion.execute('ALTER TABLE calendario ADD COLUMN proyecto_id INTEGER REFERENCES proyectos(id)')
        except sqlite3.OperationalError:
            pass
    for columna in ('hora_inicio', 'hora_fin'):
        if columna not in columnas_cal:
            try:  # hora opcional (HH:MM), p. ex. una formació de 9:00 a 14:00; '' = tot el dia
                conexion.execute(f"ALTER TABLE calendario ADD COLUMN {columna} TEXT NOT NULL DEFAULT ''")
            except sqlite3.OperationalError:
                pass  # l'altre procés de gunicorn l'ha afegit alhora
    if 'plantilla' not in columnas:
        # 1 = compta per a l'avís de falta de personal
        try:
            conexion.execute('ALTER TABLE usuarios ADD COLUMN plantilla INTEGER NOT NULL DEFAULT 1')
        except sqlite3.OperationalError:
            pass  # l'altre procés de gunicorn l'ha afegit alhora
    for clave, valor in AJUSTES_INICIALES.items():
        conexion.execute('INSERT OR IGNORE INTO ajustes (clave, valor) VALUES (?, ?)', (clave, valor))
    if not conexion.execute("SELECT 1 FROM ajustes WHERE clave = 'festius_carregats'").fetchone():
        conexion.executemany('INSERT OR IGNORE INTO festius (fecha, nombre) VALUES (?, ?)', FESTIUS_INICIALES)
        conexion.execute("INSERT OR IGNORE INTO ajustes (clave, valor) VALUES ('festius_carregats', '1')")
    conexion.commit()
    conexion.close()


crear_tablas_calendario()


def leer_ajustes(conexion):
    ajustes = dict(AJUSTES_INICIALES)
    ajustes.update({f['clave']: f['valor'] for f in conexion.execute('SELECT clave, valor FROM ajustes')})
    return {'minim_presents': int(ajustes['minim_presents']), 'patro_pelagia': ajustes['patro_pelagia']}


def fecha_valida(texto):
    try:
        return date.fromisoformat(texto) if PATRON_FECHA.match(texto or '') else None
    except ValueError:
        return None


def hora_valida(texto):
    """'HH:MM' (00:00-23:59) o '' si no n'hi ha. None = no vàlida."""
    texto = str(texto or '').strip()
    if not texto:
        return ''
    try:
        hora, minuto = (int(x) for x in texto.split(':'))
    except ValueError:
        return None
    if not (0 <= hora <= 23 and 0 <= minuto <= 59) or len(texto.split(':')[1]) != 2:
        return None
    return f'{hora:02d}:{minuto:02d}'


def validar_rango(datos):
    """Comprova inici i fi (AAAA-MM-DD, fi >= inici). Retorna (inicio, fin, error)."""
    inicio = fecha_valida(str(datos.get('inicio', '')).strip())
    fin_texto = str(datos.get('fin') or datos.get('inicio') or '').strip()
    fin = fecha_valida(fin_texto)
    if not inicio or not fin:
        return None, None, "Fecha no válida (AAAA-MM-DD)"
    if fin < inicio:
        return None, None, "La fecha final es anterior a la inicial"
    if (fin - inicio).days > 366:
        return None, None, "El periodo no puede superar un año"
    return inicio.isoformat(), fin.isoformat(), None


def dias_entre(inicio, fin):
    dia, ultimo = date.fromisoformat(inicio), date.fromisoformat(fin)
    while dia <= ultimo:
        yield dia.isoformat()
        dia += timedelta(days=1)


def usuario_existe(conexion, usuario_id):
    return conexion.execute('SELECT 1 FROM usuarios WHERE id = ? AND activo = 1', (usuario_id,)).fetchone() is not None


def puede_editar_calendario(fila):
    if session.get('es_admin'):
        return True
    yo = session.get('usuario_id')
    return yo is not None and yo in (fila['usuario_id'], fila['creado_por'])


def calcular_avisos(conexion, desde, hasta):
    """Avisos del periode: falta de personal, recursos reservats dues vegades,
    Pelagia reservada quan el patró no hi és, una persona amb dos compromisos alhora,
    el responsable d'una reserva absent i instruments en manteniment reservats.
    Caps de setmana i festius no compten."""
    ajustes = leer_ajustes(conexion)
    festius = {f['fecha'] for f in conexion.execute(
        'SELECT fecha FROM festius WHERE fecha BETWEEN ? AND ?', (desde, hasta))}
    plantilla = {f['id']: f['nombre'] for f in conexion.execute(
        'SELECT id, nombre FROM usuarios WHERE activo = 1 AND plantilla = 1')}
    entradas = conexion.execute(
        '''SELECT c.id, c.usuario_id, c.tipo, c.inicio, c.fin, c.nota, c.hora_inicio, c.hora_fin,
                  u.nombre AS persona, p.titulo AS proyecto
           FROM calendario c LEFT JOIN usuarios u ON u.id = c.usuario_id LEFT JOIN proyectos p ON p.id = c.proyecto_id
           WHERE c.inicio <= ? AND c.fin >= ? ORDER BY c.inicio, c.id''',
        (hasta, desde)).fetchall()
    reservas = conexion.execute(
        '''SELECT r.*, i.nombre AS instrumento, i.estado AS estado_instrumento, u.nombre AS persona FROM reservas r
           LEFT JOIN instrumentos i ON i.id = r.instrumento_id LEFT JOIN usuarios u ON u.id = r.usuario_id
           WHERE r.inicio <= ? AND r.fin >= ? ORDER BY r.inicio, r.id''', (hasta, desde)).fetchall()
    patron = conexion.execute('SELECT id, nombre FROM usuarios WHERE usuario = ? AND activo = 1',
                              (ajustes['patro_pelagia'],)).fetchone()

    def laborable(dia):
        return dia not in festius and date.fromisoformat(dia).weekday() < 5

    def fuera(usuario_id, dia, tipos):
        return any(e['usuario_id'] == usuario_id and e['tipo'] in tipos and e['inicio'] <= dia <= e['fin']
                   for e in entradas)

    avisos = []
    # 1. Falta de personal
    if plantilla:
        for dia in dias_entre(desde, hasta):
            if not laborable(dia):
                continue
            presentes = [u for u in plantilla if not fuera(u, dia, FUERA_DEL_CENTRO)]
            if len(presentes) < ajustes['minim_presents']:
                avisos.append({'id': f'personal:{dia}', 'tipo': 'personal', 'fecha': dia,
                               'datos': {'presentes': len(presentes), 'total': len(plantilla)},
                               'texto': f"Només {len(presentes)} de {len(plantilla)} persones al centre"})

    # 2. El mateix recurs reservat dues vegades els mateixos dies
    for i, a in enumerate(reservas):
        for b in reservas[i + 1:]:
            if a['recurso'] != b['recurso'] or (a['recurso'] == 'instrument' and a['instrumento_id'] != b['instrumento_id']):
                continue
            inicio, fin = max(a['inicio'], b['inicio']), min(a['fin'], b['fin'])
            if inicio > fin:
                continue
            nombre = a['instrumento'] or 'instrument' if a['recurso'] == 'instrument' else NOMBRE_RECURSO[a['recurso']]
            avisos.append({'id': f"conflicte:{a['id']}-{b['id']}", 'tipo': 'conflicte',
                           'fecha': max(inicio, desde), 'fin': fin,
                           'datos': {'recurso': a['recurso'], 'instrumento': a['instrumento']},
                           'texto': f"{nombre}: dues reserves els mateixos dies"})

    # 3. Pelagia reservada sense el patró
    for r in reservas:
        if r['recurso'] != 'pelagia':
            continue
        if not patron:
            avisos.append({'id': f"patro:{r['id']}", 'tipo': 'patro', 'fecha': max(r['inicio'], desde), 'datos': {},
                           'texto': "Pelagia reservada: no hi ha cap patró configurat"})
            continue
        dias = [d for d in dias_entre(max(r['inicio'], desde), min(r['fin'], hasta))
                if fuera(patron['id'], d, AUSENCIAS_PATRON)]
        if dias:
            avisos.append({'id': f"patro:{r['id']}:{dias[0]}", 'tipo': 'patro', 'fecha': dias[0], 'fin': dias[-1],
                           'datos': {'persona': patron['nombre']},
                           'texto': f"Pelagia reservada però {patron['nombre']} (patró) no hi és"})
    # 4. Una persona amb dos compromisos fora del centre els mateixos dies
    #    (p. ex. una campanya i un congrés, o dues campanyes diferents)
    fuera_de = [e for e in entradas if e['usuario_id'] is not None and e['tipo'] in FUERA_DEL_CENTRO]
    for i, a in enumerate(fuera_de):
        for b in fuera_de[i + 1:]:
            if a['usuario_id'] != b['usuario_id']:
                continue
            if a['tipo'] == b['tipo'] and (a['nota'] or '').strip().lower() == (b['nota'] or '').strip().lower():
                continue  # la mateixa cosa apuntada dues vegades
            inicio, fin = max(a['inicio'], b['inicio'], desde), min(a['fin'], b['fin'], hasta)
            if inicio > fin:
                continue
            que = lambda e: ETIQUETAS_CALENDARIO[e['tipo']] + ''.join(f" ({x})" for x in (e['nota'], e['proyecto']) if x)
            datos_e = lambda e: {'tipo': e['tipo'], 'nota': e['nota'], 'proyecto': e['proyecto']}
            avisos.append({'id': f"persona:{a['id']}-{b['id']}", 'tipo': 'persona', 'fecha': inicio, 'fin': fin,
                           'datos': {'persona': a['persona'], 'a': datos_e(a), 'b': datos_e(b)},
                           'texto': f"{a['persona']}: {que(a)} i {que(b)} coincideixen"})

    # 5. El responsable d'una reserva no hi és (a la Pelagia, una campanya pot ser la mateixa sortida)
    for r in reservas:
        if r['usuario_id'] is None or (r['recurso'] == 'pelagia' and patron and r['usuario_id'] == patron['id']):
            continue  # sense responsable de l'equip, o ja ho cobreix l'avís del patró
        tipos = FUERA_DEL_CENTRO - ({'campanya'} if r['recurso'] == 'pelagia' else set())
        dias = [d for d in dias_entre(max(r['inicio'], desde), min(r['fin'], hasta))
                if laborable(d) and fuera(r['usuario_id'], d, tipos)]
        if dias:
            nombre = (r['instrumento'] or 'Instrument') if r['recurso'] == 'instrument' else NOMBRE_RECURSO[r['recurso']]
            avisos.append({'id': f"responsable:{r['id']}:{dias[0]}", 'tipo': 'responsable', 'fecha': dias[0], 'fin': dias[-1],
                           'datos': {'recurso': r['recurso'], 'instrumento': r['instrumento'], 'persona': r['persona']},
                           'texto': f"{nombre}: reservat per {r['persona']}, que no hi serà"})

    # 6. Instrument reservat que està en manteniment o reparació
    for r in reservas:
        estado = (r['estado_instrumento'] or '').lower()
        if r['recurso'] == 'instrument' and ('manten' in estado or 'repar' in estado):
            avisos.append({'id': f"estat:{r['id']}", 'tipo': 'estat', 'fecha': max(r['inicio'], desde), 'fin': min(r['fin'], hasta),
                           'datos': {'instrumento': r['instrumento'], 'estado': r['estado_instrumento']},
                           'texto': f"{r['instrumento']}: reservat però està en «{r['estado_instrumento']}»"})

    avisos.sort(key=lambda a: (a['fecha'], a['tipo']))
    return avisos


ETIQUETAS_CALENDARIO = {'teletreball': 'teletreball', 'campanya': 'campanya', 'vacances': 'vacances',
                        'baixa': 'baixa', 'formacio': 'formació', 'reunio': 'reunió', 'altres': 'altres'}
NOMBRE_RECURSO = {'pelagia': 'Pelagia', 'tanc': 'Tanc de proves', 'instrument': 'Instrument'}


@app.route('/api/calendario', methods=['GET'])
@requiere_login
def ver_calendario():
    desde = fecha_valida(request.args.get('desde', ''))
    hasta = fecha_valida(request.args.get('hasta', ''))
    if not desde or not hasta or hasta < desde or (hasta - desde).days > MAX_DIAS_CONSULTA:
        return jsonify({"error": "Periodo no válido"}), 400
    desde, hasta = desde.isoformat(), hasta.isoformat()
    conexion = conectar_bd()
    entradas = conexion.execute(
        '''SELECT c.*, u.nombre AS persona, p.titulo AS proyecto FROM calendario c
           LEFT JOIN usuarios u ON u.id = c.usuario_id LEFT JOIN proyectos p ON p.id = c.proyecto_id
           WHERE c.inicio <= ? AND c.fin >= ? ORDER BY c.inicio, c.id''', (hasta, desde)).fetchall()
    reservas = conexion.execute(
        '''SELECT r.*, u.nombre AS persona, i.nombre AS instrumento FROM reservas r
           LEFT JOIN usuarios u ON u.id = r.usuario_id LEFT JOIN instrumentos i ON i.id = r.instrumento_id
           WHERE r.inicio <= ? AND r.fin >= ? ORDER BY r.inicio, r.id''', (hasta, desde)).fetchall()
    festius = conexion.execute(
        'SELECT fecha, nombre FROM festius WHERE fecha BETWEEN ? AND ? ORDER BY fecha', (desde, hasta)).fetchall()
    equipo = conexion.execute(
        'SELECT id, usuario, nombre, plantilla FROM usuarios WHERE activo = 1 ORDER BY nombre').fetchall()
    respuesta = {
        'entradas': [dict(e, editable=puede_editar_calendario(e)) for e in entradas],
        'reservas': [dict(r, editable=puede_editar_calendario(r)) for r in reservas],
        'festius': [dict(f) for f in festius],
        'equipo': [dict(u) for u in equipo],
        'ajustes': leer_ajustes(conexion),
        'avisos': calcular_avisos(conexion, desde, hasta),
    }
    conexion.close()
    return jsonify(respuesta)


def validar_entrada(conexion, datos):
    tipo = datos.get('tipo')
    if tipo not in TIPOS_CALENDARIO:
        return None, "Tipo no válido"
    inicio, fin, error = validar_rango(datos)
    if error:
        return None, error
    nota = str(datos.get('nota', '') or '').strip()
    if len(nota) > 500:
        return None, "La nota es demasiado larga (máximo 500 caracteres)"
    hora_inicio, hora_fin = hora_valida(datos.get('hora_inicio')), hora_valida(datos.get('hora_fin'))
    if hora_inicio is None or hora_fin is None:
        return None, "Hora no válida (HH:MM)"
    if hora_fin and not hora_inicio:
        return None, "Pon también la hora de inicio"
    if hora_fin and inicio == fin and hora_fin <= hora_inicio:
        return None, "La hora final es anterior a la inicial"
    usuario_id = datos.get('usuario_id', session.get('usuario_id'))
    if usuario_id in ('', None):
        # Entrada per a tot l'equip: només reunions i altres (no treu ningú del centre)
        if tipo not in ('reunio', 'altres'):
            return None, "Elige la persona"
        usuario_id = None
    else:
        try:
            usuario_id = int(usuario_id)
        except (TypeError, ValueError):
            return None, "Persona no válida"
        if not usuario_existe(conexion, usuario_id):
            return None, "La persona no existe"
        if not session.get('es_admin') and usuario_id != session.get('usuario_id'):
            return None, "Solo puedes apuntar tus propios días"
    proyecto_id = datos.get('proyecto_id')
    if proyecto_id in ('', None):
        proyecto_id = None
    else:
        try:
            proyecto_id = int(proyecto_id)
        except (TypeError, ValueError):
            return None, "Proyecto no válido"
        if not conexion.execute('SELECT 1 FROM proyectos WHERE id = ?', (proyecto_id,)).fetchone():
            return None, "El proyecto no existe"
    return (usuario_id, tipo, inicio, fin, nota, proyecto_id, hora_inicio, hora_fin), None


@app.route('/api/calendario/entradas', methods=['POST'])
@requiere_login
def crear_entrada_calendario():
    conexion = conectar_bd()
    valores, error = validar_entrada(conexion, request.get_json(silent=True) or {})
    if error:
        conexion.close()
        return jsonify({"error": error}), 400
    cursor = conexion.execute(
        'INSERT INTO calendario (usuario_id, tipo, inicio, fin, nota, proyecto_id, hora_inicio, hora_fin, creado_por)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        valores + (session.get('usuario_id'),))
    conexion.commit()
    conexion.close()
    return jsonify({"id": cursor.lastrowid}), 201


@app.route('/api/calendario/entradas/<int:id>', methods=['PUT', 'DELETE'])
@requiere_login
def modificar_entrada_calendario(id):
    conexion = conectar_bd()
    fila = conexion.execute('SELECT * FROM calendario WHERE id = ?', (id,)).fetchone()
    if not fila:
        conexion.close()
        return jsonify({"error": "No existe"}), 404
    if not puede_editar_calendario(fila):
        conexion.close()
        return jsonify({"error": "Solo puedes cambiar tus propias entradas"}), 403
    if request.method == 'DELETE':
        conexion.execute('DELETE FROM calendario WHERE id = ?', (id,))
    else:
        datos = request.get_json(silent=True) or {}
        datos.setdefault('usuario_id', fila['usuario_id'])
        datos.setdefault('proyecto_id', fila['proyecto_id'])
        datos.setdefault('hora_inicio', fila['hora_inicio'])
        datos.setdefault('hora_fin', fila['hora_fin'])
        valores, error = validar_entrada(conexion, datos)
        if error:
            conexion.close()
            return jsonify({"error": error}), 400
        conexion.execute('UPDATE calendario SET usuario_id = ?, tipo = ?, inicio = ?, fin = ?, nota = ?, proyecto_id = ?,'
                         ' hora_inicio = ?, hora_fin = ? WHERE id = ?',
                         valores + (id,))
    conexion.commit()
    conexion.close()
    return ('', 204) if request.method == 'DELETE' else jsonify({"id": id})


def validar_reserva(conexion, datos):
    recurso = datos.get('recurso')
    if recurso not in RECURSOS:
        return None, "Recurso no válido"
    instrumento_id = None
    if recurso == 'instrument':
        try:
            instrumento_id = int(datos.get('instrumento_id'))
        except (TypeError, ValueError):
            return None, "Elige el instrumento"
        if not conexion.execute('SELECT 1 FROM instrumentos WHERE id = ?', (instrumento_id,)).fetchone():
            return None, "El instrumento no existe"
    inicio, fin, error = validar_rango(datos)
    if error:
        return None, error
    para = str(datos.get('para', '') or '').strip()
    proposito = str(datos.get('proposito', '') or '').strip()
    if len(para) > 200 or len(proposito) > 500:
        return None, "Texto demasiado largo"
    usuario_id = datos.get('usuario_id', session.get('usuario_id'))
    if usuario_id in ('', None):
        usuario_id = None
    else:
        try:
            usuario_id = int(usuario_id)
        except (TypeError, ValueError):
            return None, "Persona no válida"
        if not usuario_existe(conexion, usuario_id):
            return None, "La persona no existe"
        if not session.get('es_admin') and usuario_id != session.get('usuario_id'):
            return None, "Solo puedes hacer reservas a tu nombre"
    if usuario_id is None and not para:
        return None, "Indica el responsable de la reserva"
    return (recurso, instrumento_id, inicio, fin, usuario_id, para, proposito), None


@app.route('/api/calendario/reservas', methods=['POST'])
@requiere_login
def crear_reserva():
    conexion = conectar_bd()
    valores, error = validar_reserva(conexion, request.get_json(silent=True) or {})
    if error:
        conexion.close()
        return jsonify({"error": error}), 400
    cursor = conexion.execute(
        '''INSERT INTO reservas (recurso, instrumento_id, inicio, fin, usuario_id, para, proposito, creado_por)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', valores + (session.get('usuario_id'),))
    conexion.commit()
    conexion.close()
    return jsonify({"id": cursor.lastrowid}), 201


@app.route('/api/calendario/reservas/<int:id>', methods=['PUT', 'DELETE'])
@requiere_login
def modificar_reserva(id):
    conexion = conectar_bd()
    fila = conexion.execute('SELECT * FROM reservas WHERE id = ?', (id,)).fetchone()
    if not fila:
        conexion.close()
        return jsonify({"error": "No existe"}), 404
    if not puede_editar_calendario(fila):
        conexion.close()
        return jsonify({"error": "Solo puedes cambiar tus propias reservas"}), 403
    if request.method == 'DELETE':
        conexion.execute('DELETE FROM reservas WHERE id = ?', (id,))
    else:
        datos = request.get_json(silent=True) or {}
        datos.setdefault('usuario_id', fila['usuario_id'])
        valores, error = validar_reserva(conexion, datos)
        if error:
            conexion.close()
            return jsonify({"error": error}), 400
        conexion.execute(
            '''UPDATE reservas SET recurso = ?, instrumento_id = ?, inicio = ?, fin = ?, usuario_id = ?,
               para = ?, proposito = ? WHERE id = ?''', valores + (id,))
    conexion.commit()
    conexion.close()
    return ('', 204) if request.method == 'DELETE' else jsonify({"id": id})


@app.route('/api/calendario/festius', methods=['GET', 'POST'])
@requiere_login
def gestionar_festius():
    conexion = conectar_bd()
    if request.method == 'GET':
        filas = conexion.execute('SELECT fecha, nombre FROM festius ORDER BY fecha').fetchall()
        conexion.close()
        return jsonify([dict(f) for f in filas])
    if not session.get('es_admin'):
        conexion.close()
        return jsonify({"error": "Solo administradores"}), 403
    datos = request.get_json(silent=True) or {}
    fecha = fecha_valida(str(datos.get('fecha', '')).strip())
    nombre = str(datos.get('nombre', '')).strip()
    if not fecha or not nombre or len(nombre) > 100:
        conexion.close()
        return jsonify({"error": "Indica la fecha y el nombre del festivo"}), 400
    conexion.execute('INSERT OR REPLACE INTO festius (fecha, nombre) VALUES (?, ?)', (fecha.isoformat(), nombre))
    conexion.commit()
    conexion.close()
    return jsonify({"fecha": fecha.isoformat()}), 201


@app.route('/api/calendario/festius/<fecha>', methods=['DELETE'])
@requiere_admin
def borrar_festiu(fecha):
    conexion = conectar_bd()
    conexion.execute('DELETE FROM festius WHERE fecha = ?', (fecha,))
    conexion.commit()
    conexion.close()
    return '', 204


@app.route('/api/calendario/ajustes', methods=['PUT'])
@requiere_admin
def cambiar_ajustes_calendario():
    datos = request.get_json(silent=True) or {}
    conexion = conectar_bd()
    if 'minim_presents' in datos:
        try:
            minimo = int(datos['minim_presents'])
        except (TypeError, ValueError):
            minimo = -1
        if not 0 <= minimo <= 50:
            conexion.close()
            return jsonify({"error": "Número de personas no válido"}), 400
        conexion.execute("INSERT OR REPLACE INTO ajustes (clave, valor) VALUES ('minim_presents', ?)", (str(minimo),))
    if 'patro_pelagia' in datos:
        patron = str(datos['patro_pelagia'] or '').strip().lower()
        if patron and not conexion.execute('SELECT 1 FROM usuarios WHERE usuario = ?', (patron,)).fetchone():
            conexion.close()
            return jsonify({"error": "Ese usuario no existe"}), 400
        conexion.execute("INSERT OR REPLACE INTO ajustes (clave, valor) VALUES ('patro_pelagia', ?)", (patron,))
    conexion.commit()
    ajustes = leer_ajustes(conexion)
    conexion.close()
    return jsonify(ajustes)


@app.route('/api/ocupacion', methods=['GET'])
def ocupacion_publica():
    """Dies ocupats d'un recurs per als calendaris públics (sense noms ni motius)."""
    recurso = request.args.get('recurso')
    if recurso not in RECURSOS:
        return jsonify({"error": "Recurso no válido"}), 400
    hoy = date.today()
    desde = fecha_valida(request.args.get('desde', '')) or hoy.replace(day=1)
    hasta = fecha_valida(request.args.get('hasta', '')) or desde + timedelta(days=MAX_DIAS_CONSULTA)
    if hasta < desde or (hasta - desde).days > MAX_DIAS_CONSULTA:
        return jsonify({"error": "Periodo no válido"}), 400
    desde, hasta = desde.isoformat(), hasta.isoformat()
    condiciones, valores = ['recurso = ?', 'inicio <= ?', 'fin >= ?'], [recurso, hasta, desde]
    if recurso == 'instrument':
        try:
            valores.append(int(request.args.get('instrumento_id')))
        except (TypeError, ValueError):
            return jsonify({"error": "Instrumento no válido"}), 400
        condiciones.append('instrumento_id = ?')
    conexion = conectar_bd()
    filas = conexion.execute(f'SELECT inicio, fin FROM reservas WHERE {" AND ".join(condiciones)}', valores).fetchall()
    conexion.close()
    dias = sorted({d for f in filas for d in dias_entre(max(f['inicio'], desde), min(f['fin'], hasta))})
    return jsonify(dias)


# ---------------------------------------------------------------------------
# Correu de cada usuari i «He oblidat la contrasenya»
# ---------------------------------------------------------------------------
# L'enllaç porta un testimoni signat amb SIO_SECRET_KEY que caduca en una hora
# i que deixa de valer quan es canvia la contrasenya (inclou un tros del hash).
# L'adreça de la web es fixa (SIO_URL_PUBLICA) perquè ningú pugui fer arribar
# un enllaç que apunti a una altra web canviant la capçalera Host.
URL_PUBLICA = os.environ.get('SIO_URL_PUBLICA', 'https://sio.icm.csic.es').rstrip('/')
VALIDEZ_ENLACE = 3600
MAX_RECUPERACIONES_POR_HORA = 5
recuperaciones_por_ip = defaultdict(deque)


def crear_columna_email():
    conexion = conectar_bd()
    columnas = [fila['name'] for fila in conexion.execute('PRAGMA table_info(usuarios)')]
    if 'email' not in columnas:
        try:
            conexion.execute('ALTER TABLE usuarios ADD COLUMN email TEXT')
        except sqlite3.OperationalError:
            pass  # l'altre procés de gunicorn l'ha afegit alhora
    conexion.commit()
    conexion.close()


crear_columna_email()


def validar_email_usuario(conexion, email, usuario_id=None):
    """Retorna (email normalitzat o None, error)."""
    email = str(email or '').strip().lower()
    if not email:
        return None, None
    if len(email) > 254 or not PATRON_EMAIL.match(email):
        return None, "Correo no válido"
    otro = conexion.execute('SELECT id FROM usuarios WHERE lower(email) = ? AND id IS NOT ?', (email, usuario_id)).fetchone()
    if otro:
        return None, "Ese correo ya lo tiene otro usuario"
    return email, None


def serializador_enlaces():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='restablir-contrasenya')


def demasiadas_recuperaciones(ip):
    ahora = time.time()
    peticiones = recuperaciones_por_ip[ip]
    while peticiones and ahora - peticiones[0] > 3600:
        peticiones.popleft()
    if len(peticiones) >= MAX_RECUPERACIONES_POR_HORA:
        return True
    peticiones.append(ahora)
    return False


@app.route('/api/recuperar', methods=['POST'])
def recuperar_contrasena():
    # Sempre la mateixa resposta: no es diu si l'usuari o el correu existeixen
    respuesta = jsonify({"mensaje": "Si existe, te hemos enviado un enlace"})
    if not login_configurado() or not os.environ.get('SIO_SMTP_HOST'):
        return jsonify({"error": "El envío de correo no está configurado"}), 503
    if demasiadas_recuperaciones(request.remote_addr):
        return jsonify({"error": "Demasiadas peticiones. Inténtalo más tarde"}), 429
    dato = str((request.get_json(silent=True) or {}).get('usuario', '')).strip().lower()
    if not dato or len(dato) > 254:
        return respuesta
    conexion = conectar_bd()
    fila = conexion.execute(
        'SELECT id, nombre, usuario, email, password_hash FROM usuarios WHERE activo = 1 AND (usuario = ? OR lower(email) = ?)',
        (dato, dato)).fetchone()
    conexion.close()
    if not fila or not fila['email']:
        return respuesta
    testimonio = serializador_enlaces().dumps({'id': fila['id'], 'h': fila['password_hash'][-12:]})
    enlace = f"{URL_PUBLICA}/intranet?restablir={testimonio}"
    mensaje = EmailMessage()
    mensaje['Subject'] = 'Intranet SIO: canvi de contrasenya'
    mensaje['From'] = os.environ.get('SIO_SMTP_FROM', CONTACTO_DESTINO)
    mensaje['To'] = fila['email']
    mensaje.set_content(
        f"Hola, {fila['nombre']}:\n\n"
        f"Algú (segurament tu) ha demanat canviar la contrasenya de la intranet del SIO.\n"
        f"El teu usuari és: {fila['usuario']}\n\n"
        f"Per posar-ne una de nova, obre aquest enllaç (val durant una hora i només una vegada):\n\n"
        f"{enlace}\n\n"
        f"Si no ho has demanat tu, no cal que facis res: la contrasenya actual continua sent vàlida.\n\n"
        f"-- \nWeb del SIO (missatge automàtic, no contestis aquest correu)\n")
    try:
        enviar_correo(mensaje)
    except Exception as e:
        print("Error enviando el enlace de recuperación:", e)
        return jsonify({"error": "No se ha podido enviar el correo. Pídelo a un administrador"}), 502
    return respuesta


@app.route('/api/restablir', methods=['POST'])
def restablecer_contrasena():
    datos = request.get_json(silent=True) or {}
    nueva = str(datos.get('nueva', ''))
    try:
        contenido = serializador_enlaces().loads(str(datos.get('token', '')), max_age=VALIDEZ_ENLACE)
    except SignatureExpired:
        return jsonify({"error": "El enlace ha caducado. Pide uno nuevo"}), 400
    except BadSignature:
        return jsonify({"error": "El enlace no es válido"}), 400
    if len(nueva) < 8:
        return jsonify({"error": "La contraseña nueva debe tener al menos 8 caracteres"}), 400
    conexion = conectar_bd()
    fila = conexion.execute('SELECT id, usuario, password_hash FROM usuarios WHERE id = ? AND activo = 1',
                            (contenido.get('id'),)).fetchone()
    if not fila or not hmac.compare_digest(fila['password_hash'][-12:], str(contenido.get('h', ''))):
        conexion.close()
        return jsonify({"error": "Este enlace ya se ha usado. Pide uno nuevo"}), 400
    conexion.execute('UPDATE usuarios SET password_hash = ?, debe_cambiar = 0 WHERE id = ?',
                     (generate_password_hash(nueva), fila['id']))
    conexion.commit()
    conexion.close()
    return jsonify({"usuario": fila['usuario']})


@app.route('/api/mi-cuenta', methods=['GET', 'PUT'])
@requiere_login
def mi_cuenta():
    usuario_id = session.get('usuario_id')
    if usuario_id is None:
        return jsonify({"email": None})
    conexion = conectar_bd()
    if request.method == 'PUT':
        email, error = validar_email_usuario(conexion, (request.get_json(silent=True) or {}).get('email'), usuario_id)
        if error:
            conexion.close()
            return jsonify({"error": error}), 400
        conexion.execute('UPDATE usuarios SET email = ? WHERE id = ?', (email, usuario_id))
        conexion.commit()
    fila = conexion.execute('SELECT email FROM usuarios WHERE id = ?', (usuario_id,)).fetchone()
    conexion.close()
    return jsonify({"email": fila['email'] if fila else None})

# ---------------------------------------------------------------------------
# Memòria anual pública: xifres de l'any a partir del diari i del calendari
# ---------------------------------------------------------------------------
# Només xifres globals: cap nom, cap text de notes internes, ni teletreball,
# vacances o baixes. Les activitats destacades són les notes ja aprovades per
# a la web (/api/diario).
@app.route('/api/memoria', methods=['GET'])
def memoria_anual():
    hoy = date.today()
    try:
        anio = int(request.args.get('anio', hoy.year))
    except ValueError:
        return jsonify({"error": "Año no válido"}), 400
    if not 2000 <= anio <= hoy.year:
        return jsonify({"error": "Año no válido"}), 400
    desde, hasta = f'{anio}-01-01', f'{anio}-12-31'
    conexion = conectar_bd()
    notas = conexion.execute('SELECT tipo, proyecto_id, horas FROM notas WHERE fecha BETWEEN ? AND ?',
                             (desde, hasta)).fetchall()
    por_tipo = {}
    for n in notas:
        por_tipo[n['tipo']] = por_tipo.get(n['tipo'], 0) + 1
    sin_proyecto = [n for n in notas if n['proyecto_id'] is None]
    horas = [INTERVALOS_HORAS[n['horas']] for n in sin_proyecto if n['horas'] in INTERVALOS_HORAS]

    def dias_distintos(filas):
        dias = set()
        for f in filas:
            dias.update(d for d in dias_entre(max(f['inicio'], desde), min(f['fin'], hasta)))
        return len(dias)

    campanyas = conexion.execute("SELECT inicio, fin FROM calendario WHERE tipo = 'campanya' AND inicio <= ? AND fin >= ?",
                                 (hasta, desde)).fetchall()
    reservas = {r: conexion.execute('SELECT inicio, fin FROM reservas WHERE recurso = ? AND inicio <= ? AND fin >= ?',
                                    (r, hasta, desde)).fetchall() for r in RECURSOS}
    primero = conexion.execute(
        'SELECT MIN(f) FROM (SELECT MIN(fecha) AS f FROM notas UNION SELECT MIN(inicio) FROM calendario '
        'UNION SELECT MIN(inicio) FROM reservas)').fetchone()[0]
    conexion.close()
    return jsonify({
        'anio': anio,
        'anios': list(range(hoy.year, int(primero[:4]) - 1, -1)) if primero else [hoy.year],
        'actividades': len(notas),
        'por_tipo': por_tipo,
        'proyectos': len({n['proyecto_id'] for n in notas if n['proyecto_id'] is not None}),
        'encargos_sin_proyecto': len(sin_proyecto),
        'horas_sin_proyecto': {'min': sum(h[0] for h in horas), 'max': sum(h[1] for h in horas)},
        'dias_campanya': dias_distintos(campanyas),
        'dias_pelagia': dias_distintos(reservas['pelagia']),
        'dias_tanque': dias_distintos(reservas['tanc']),
        'prestamos': len(reservas['instrument']),
    })


# =======================================================
# EQUIPO (fichas de la página pública «Equipo SIO», editables desde la intranet)
# =======================================================
EQUIPO_DIR = os.path.join(os.path.dirname(DB_PATH), 'equipo')
EQUIPO_INICIAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'equipo_inicial.json')
IDIOMAS = ('ca', 'es', 'en')
ETIQUETAS_EQUIPO = ('liderazgo', 'ingenieria', 'soporte')
CAMPOS_EQUIPO = ['nombre', 'email', 'etiqueta', 'orden', 'visible'] + \
    [f'{c}_{l}' for c in ('cargo', 'descripcion') for l in IDIOMAS]


def crear_tablas_equipo_docs():
    conexion = conectar_bd()
    conexion.executescript(f"""
        CREATE TABLE IF NOT EXISTS equipo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden INTEGER NOT NULL DEFAULT 0,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL DEFAULT '',
            etiqueta TEXT NOT NULL DEFAULT 'soporte',
            foto TEXT NOT NULL DEFAULT '',
            visible INTEGER NOT NULL DEFAULT 1,
            {', '.join(f"{c}_{l} TEXT NOT NULL DEFAULT ''" for c in ('cargo', 'descripcion') for l in IDIOMAS)},
            actualizado TEXT
        );
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT NOT NULL DEFAULT '',
            categoria TEXT NOT NULL,
            fabricante TEXT NOT NULL DEFAULT '',
            formato TEXT NOT NULL,
            archivo TEXT NOT NULL,
            nombre_original TEXT NOT NULL,
            tamano INTEGER NOT NULL DEFAULT 0,
            usuario_id INTEGER,
            subido_por TEXT NOT NULL,
            creado TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS equipo_cargado (id INTEGER PRIMARY KEY CHECK (id = 1));
    """)
    # La primera vez se cargan las fichas que había en la web (una sola vez, aunque
    # los dos procesos de gunicorn arranquen a la vez)
    try:
        conexion.execute('BEGIN IMMEDIATE')
        if not conexion.execute('SELECT 1 FROM equipo_cargado').fetchone():
            with open(EQUIPO_INICIAL, encoding='utf-8') as f:
                for p in json_lib.load(f):
                    campos = list(p)
                    conexion.execute(
                        f"INSERT INTO equipo ({', '.join(campos)}) VALUES ({', '.join('?' * len(campos))})",
                        [p[c] for c in campos])
            conexion.execute('INSERT INTO equipo_cargado (id) VALUES (1)')
        conexion.commit()
    except sqlite3.OperationalError:
        conexion.rollback()
    conexion.close()
    os.makedirs(EQUIPO_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)


def ficha_equipo(fila):
    d = dict(fila)
    d['visible'] = bool(d['visible'])
    return d


def validar_ficha(datos, actual=None):
    ficha = dict(actual) if actual else {'orden': 99, 'visible': 1, 'email': '', 'etiqueta': 'soporte'}
    for campo in CAMPOS_EQUIPO:
        if campo in datos:
            ficha[campo] = datos[campo]
    ficha['nombre'] = str(ficha.get('nombre') or '').strip()
    if not ficha['nombre'] or len(ficha['nombre']) > 100:
        return None, "El nombre es obligatorio"
    ficha['email'] = str(ficha.get('email') or '').strip()
    if ficha['email'] and not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', ficha['email']):
        return None, "Correo no válido"
    if ficha.get('etiqueta') not in ETIQUETAS_EQUIPO:
        return None, "Grupo no válido"
    try:
        ficha['orden'] = int(ficha.get('orden') or 0)
    except (TypeError, ValueError):
        return None, "Orden no válido"
    ficha['visible'] = 1 if ficha.get('visible') in (True, 1, '1') else 0
    for l in IDIOMAS:
        ficha[f'cargo_{l}'] = str(ficha.get(f'cargo_{l}') or '').strip()[:200]
        ficha[f'descripcion_{l}'] = str(ficha.get(f'descripcion_{l}') or '').strip()[:1500]
    if not any(ficha[f'cargo_{l}'] for l in IDIOMAS):
        return None, "Falta el cargo"
    return ficha, None


def borrar_foto_equipo(foto):
    if foto and foto.startswith('/api/equipo/fotos/'):
        try:
            os.remove(os.path.join(EQUIPO_DIR, foto.rsplit('/', 1)[1]))
        except FileNotFoundError:
            pass


@app.route('/api/equipo', methods=['GET', 'POST'])
def gestionar_equipo():
    if request.method == 'GET':
        # La web pública ve solo las fichas visibles; la intranet (?todas=1) las ve todas
        todas = request.args.get('todas') and session.get('autenticado')
        conexion = conectar_bd()
        filas = conexion.execute(
            'SELECT * FROM equipo' + ('' if todas else ' WHERE visible = 1') + ' ORDER BY orden, id').fetchall()
        conexion.close()
        fichas = [ficha_equipo(f) for f in filas]
        if not session.get('autenticado'):
            for f in fichas:
                f.pop('email', None)
        return jsonify(fichas)
    return crear_ficha_equipo()


@requiere_login
def crear_ficha_equipo():
    ficha, error = validar_ficha(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400
    campos = CAMPOS_EQUIPO
    conexion = conectar_bd()
    cursor = conexion.execute(
        f"INSERT INTO equipo ({', '.join(campos)}, actualizado) VALUES ({', '.join('?' * len(campos))}, datetime('now'))",
        [ficha[c] for c in campos])
    conexion.commit()
    fila = conexion.execute('SELECT * FROM equipo WHERE id = ?', (cursor.lastrowid,)).fetchone()
    conexion.close()
    return jsonify(ficha_equipo(fila)), 201


@app.route('/api/equipo/<int:id>', methods=['PUT', 'DELETE'])
@requiere_login
def modificar_ficha_equipo(id):
    conexion = conectar_bd()
    actual = conexion.execute('SELECT * FROM equipo WHERE id = ?', (id,)).fetchone()
    if not actual:
        conexion.close()
        return jsonify({"error": "No existe"}), 404
    if request.method == 'DELETE':
        if not session.get('es_admin'):
            conexion.close()
            return jsonify({"error": "Solo para administradores"}), 403
        conexion.execute('DELETE FROM equipo WHERE id = ?', (id,))
        conexion.commit()
        conexion.close()
        borrar_foto_equipo(actual['foto'])
        return '', 204
    ficha, error = validar_ficha(request.get_json(silent=True) or {}, actual)
    if error:
        conexion.close()
        return jsonify({"error": error}), 400
    conexion.execute(
        f"UPDATE equipo SET {', '.join(c + ' = ?' for c in CAMPOS_EQUIPO)}, actualizado = datetime('now') WHERE id = ?",
        [ficha[c] for c in CAMPOS_EQUIPO] + [id])
    conexion.commit()
    fila = conexion.execute('SELECT * FROM equipo WHERE id = ?', (id,)).fetchone()
    conexion.close()
    return jsonify(ficha_equipo(fila))


@app.route('/api/equipo/<int:id>/foto', methods=['POST'])
@requiere_login
def subir_foto_equipo(id):
    conexion = conectar_bd()
    actual = conexion.execute('SELECT foto FROM equipo WHERE id = ?', (id,)).fetchone()
    if not actual:
        conexion.close()
        return jsonify({"error": "No existe"}), 404
    fichero = request.files.get('foto')
    if not fichero:
        conexion.close()
        return jsonify({"error": "No se ha recibido ninguna foto"}), 400
    try:
        imagen = Image.open(fichero.stream)
        imagen.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        conexion.close()
        return jsonify({"error": "El archivo no es una imagen"}), 400
    # Cuadrada y centrada (la web la enseña en un círculo); sin EXIF
    imagen = ImageOps.exif_transpose(imagen)
    if imagen.mode not in ('RGB', 'RGBA'):
        imagen = imagen.convert('RGB')
    imagen = ImageOps.fit(imagen, (600, 600), centering=(0.5, 0.35))
    nombre = uuid.uuid4().hex + '.webp'
    imagen.save(os.path.join(EQUIPO_DIR, nombre), 'WEBP', quality=82, method=4)
    url = '/api/equipo/fotos/' + nombre
    conexion.execute("UPDATE equipo SET foto = ?, actualizado = datetime('now') WHERE id = ?", (url, id))
    conexion.commit()
    conexion.close()
    borrar_foto_equipo(actual['foto'])
    return jsonify({"foto": url}), 201


@app.route('/api/equipo/fotos/<nombre>', methods=['GET'])
def foto_equipo(nombre):
    if not re.fullmatch(r'[0-9a-f]{32}\.webp', nombre):
        return jsonify({"error": "No existe"}), 404
    return send_from_directory(EQUIPO_DIR, nombre, mimetype='image/webp', max_age=86400)


# =======================================================
# BIBLIOTECA DE DOCUMENTOS (archivos subidos desde la intranet; solo para el equipo)
# =======================================================
DOCS_DIR = os.path.join(os.path.dirname(DB_PATH), 'documentos')
EXTENSIONES_DOC = {
    'pdf': 'PDF', 'doc': 'DOC', 'docx': 'DOC', 'odt': 'DOC', 'rtf': 'DOC', 'txt': 'TXT',
    'xls': 'XLS', 'xlsx': 'XLS', 'ods': 'XLS', 'csv': 'XLS',
    'ppt': 'PPT', 'pptx': 'PPT', 'odp': 'PPT',
    'jpg': 'JPG', 'jpeg': 'JPG', 'png': 'PNG',
    'zip': 'ZIP', '7z': 'ZIP', 'rar': 'ZIP',
}
# Estos se abren en el navegador; el resto se descarga
EXTENSIONES_EN_LINEA = {'pdf', 'jpg', 'jpeg', 'png', 'txt'}


def puede_editar_doc(doc):
    if session.get('es_admin'):
        return True
    return doc['usuario_id'] is not None and doc['usuario_id'] == session.get('usuario_id')


def documento_json(fila):
    d = dict(fila)
    d.pop('archivo', None)
    d['enlace'] = f"/api/documentos/{d['id']}/archivo"
    d['puede_editar'] = puede_editar_doc(fila)
    return d


def validar_doc(datos, actual=None):
    doc = {c: (actual[c] if actual else '') for c in ('titulo', 'descripcion', 'categoria', 'fabricante')}
    for c in doc:
        if c in datos:
            doc[c] = str(datos[c] or '').strip()
    if not doc['titulo'] or not doc['categoria']:
        return None, "Rellena los campos obligatorios"
    if len(doc['titulo']) > 200 or len(doc['categoria']) > 100 or len(doc['fabricante']) > 100:
        return None, "Texto demasiado largo"
    doc['descripcion'] = doc['descripcion'][:2000]
    return doc, None


@app.route('/api/documentos', methods=['GET', 'POST'])
@requiere_login
def gestionar_documentos():
    conexion = conectar_bd()
    if request.method == 'GET':
        filas = conexion.execute('SELECT * FROM documentos ORDER BY categoria, fabricante, titulo').fetchall()
        conexion.close()
        return jsonify([documento_json(f) for f in filas])
    doc, error = validar_doc(request.form)
    fichero = request.files.get('archivo')
    if not error and not fichero:
        error = "No se ha recibido ningún archivo"
    extension = fichero.filename.rsplit('.', 1)[-1].lower() if fichero and '.' in fichero.filename else ''
    if not error and extension not in EXTENSIONES_DOC:
        error = "Tipo de archivo no permitido"
    if error:
        conexion.close()
        return jsonify({"error": error}), 400
    nombre = f'{uuid.uuid4().hex}.{extension}'
    ruta = os.path.join(DOCS_DIR, nombre)
    fichero.save(ruta)
    original = os.path.basename(fichero.filename.replace('\\', '/'))[:200] or nombre
    cursor = conexion.execute(
        'INSERT INTO documentos (titulo, descripcion, categoria, fabricante, formato, archivo, nombre_original, '
        'tamano, usuario_id, subido_por) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (doc['titulo'], doc['descripcion'], doc['categoria'], doc['fabricante'], EXTENSIONES_DOC[extension],
         nombre, original, os.path.getsize(ruta), session.get('usuario_id'), session.get('nombre') or ''))
    conexion.commit()
    fila = conexion.execute('SELECT * FROM documentos WHERE id = ?', (cursor.lastrowid,)).fetchone()
    conexion.close()
    return jsonify(documento_json(fila)), 201


@app.route('/api/documentos/<int:id>', methods=['PUT', 'DELETE'])
@requiere_login
def modificar_documento(id):
    conexion = conectar_bd()
    actual = conexion.execute('SELECT * FROM documentos WHERE id = ?', (id,)).fetchone()
    if not actual:
        conexion.close()
        return jsonify({"error": "No existe"}), 404
    if not puede_editar_doc(actual):
        conexion.close()
        return jsonify({"error": "Solo puede cambiarlo quien lo subió o un administrador"}), 403
    if request.method == 'DELETE':
        conexion.execute('DELETE FROM documentos WHERE id = ?', (id,))
        conexion.commit()
        conexion.close()
        try:
            os.remove(os.path.join(DOCS_DIR, actual['archivo']))
        except FileNotFoundError:
            pass
        return '', 204
    doc, error = validar_doc(request.get_json(silent=True) or {}, actual)
    if error:
        conexion.close()
        return jsonify({"error": error}), 400
    conexion.execute('UPDATE documentos SET titulo = ?, descripcion = ?, categoria = ?, fabricante = ? WHERE id = ?',
                     (doc['titulo'], doc['descripcion'], doc['categoria'], doc['fabricante'], id))
    conexion.commit()
    fila = conexion.execute('SELECT * FROM documentos WHERE id = ?', (id,)).fetchone()
    conexion.close()
    return jsonify(documento_json(fila))


@app.route('/api/documentos/<int:id>/archivo', methods=['GET'])
@requiere_login
def archivo_documento(id):
    conexion = conectar_bd()
    fila = conexion.execute('SELECT archivo, nombre_original FROM documentos WHERE id = ?', (id,)).fetchone()
    conexion.close()
    if not fila:
        return jsonify({"error": "No existe"}), 404
    extension = fila['archivo'].rsplit('.', 1)[-1]
    respuesta = send_from_directory(DOCS_DIR, fila['archivo'], download_name=fila['nombre_original'],
                                    as_attachment=extension not in EXTENSIONES_EN_LINEA, max_age=0)
    respuesta.headers['Cache-Control'] = 'private, no-cache'
    respuesta.headers['X-Content-Type-Options'] = 'nosniff'
    return respuesta


crear_tablas_equipo_docs()


# ---------------------------------------------------------------------------
# COMPRES SENSE PROJECTE
# Llista compartida del que cal comprar sense projecte (sobretot a RS). Quan els
# articles de RS pendents arriben a COMPRAS_MINIMO € (sense IVA), RS no cobra els
# ports (~16 €) i es pot enviar la llista a RS per demanar-ne pressupost.
# ---------------------------------------------------------------------------
COMPRAS_MINIMO = float(os.environ.get('SIO_COMPRAS_MINIMO', '95'))
COMPRAS_DESTINO = os.environ.get('SIO_COMPRAS_DESTINO', 'Ofertas@rs.rsgroup.com')
COMPRAS_PROVEEDOR = 'RS Components'
COMPRAS_PORTES = 16  # el que ens estalviem arribant al mínim (només informatiu)


def crear_tablas_compras():
    conexion = conectar_bd()
    conexion.executescript("""
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL DEFAULT (date('now')),
            usuario_id INTEGER REFERENCES usuarios(id),
            pedido_por TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 1,
            proveedor TEXT NOT NULL DEFAULT 'RS Components',
            referencia TEXT NOT NULL DEFAULT '',
            precio REAL,                          -- preu unitari sense IVA (NULL = encara no se sap)
            envio_id INTEGER REFERENCES compras_envios(id),  -- NULL = pendent
            creado TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS compras_envios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL DEFAULT (datetime('now')),
            enviado_por TEXT NOT NULL,
            destinatario TEXT NOT NULL,
            total REAL NOT NULL,
            articulos INTEGER NOT NULL
        );
    """)
    conexion.commit()
    conexion.close()


crear_tablas_compras()


def es_rs(proveedor):
    # «RS Components», «RS», «RS-Online»... (la paraula «rs» dins del nom)
    return 'rs' in re.split(r'[^a-z0-9]+', (proveedor or '').lower())


def resumen_compras(conexion):
    pendientes = [dict(f) for f in conexion.execute(
        'SELECT * FROM compras WHERE envio_id IS NULL ORDER BY fecha, id')]
    for f in pendientes:
        f['editable'] = bool(session.get('es_admin')) or f['usuario_id'] == session.get('usuario_id')
        f['es_rs'] = es_rs(f['proveedor'])
    rs = [f for f in pendientes if f['es_rs']]
    total = round(sum((f['precio'] or 0) * f['cantidad'] for f in rs), 2)
    envios = [dict(e) for e in conexion.execute('SELECT * FROM compras_envios ORDER BY id DESC LIMIT 20')]
    for e in envios:
        e['items'] = [dict(f) for f in conexion.execute(
            'SELECT descripcion, cantidad, referencia, precio, pedido_por FROM compras WHERE envio_id = ? ORDER BY id', (e['id'],))]
    return {
        'pendientes': pendientes,
        'total_rs': total,
        'sin_precio_rs': sum(1 for f in rs if f['precio'] is None),
        'minimo': COMPRAS_MINIMO,
        'portes': COMPRAS_PORTES,
        'destino': COMPRAS_DESTINO,
        'envios': envios,
        'correo_configurado': bool(os.environ.get('SIO_SMTP_HOST')),
    }


def validar_compra(datos):
    descripcion = str(datos.get('descripcion', '') or '').strip()
    proveedor = str(datos.get('proveedor', '') or '').strip() or COMPRAS_PROVEEDOR
    referencia = str(datos.get('referencia', '') or '').strip()
    if not descripcion:
        return None, "Escribe qué se necesita"
    if len(descripcion) > 300 or len(proveedor) > 100 or len(referencia) > 60:
        return None, "Algún campo es demasiado largo"
    try:
        cantidad = int(datos.get('cantidad', 1))
    except (TypeError, ValueError):
        return None, "Cantidad no válida"
    if not 1 <= cantidad <= 9999:
        return None, "Cantidad no válida"
    precio = datos.get('precio')
    if precio in ('', None):
        precio = None
    else:
        try:
            precio = round(float(str(precio).replace(',', '.')), 2)
        except ValueError:
            return None, "Precio no válido"
        if not 0 <= precio <= 100000:
            return None, "Precio no válido"
    return (descripcion, cantidad, proveedor, referencia, precio), None


@app.route('/api/compras', methods=['GET', 'POST'])
@requiere_login
def gestionar_compras():
    conexion = conectar_bd()
    if request.method == 'POST':
        valores, error = validar_compra(request.get_json(silent=True) or {})
        if error:
            conexion.close()
            return jsonify({"error": error}), 400
        conexion.execute(
            'INSERT INTO compras (usuario_id, pedido_por, descripcion, cantidad, proveedor, referencia, precio)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?)',
            (session.get('usuario_id'), session.get('nombre') or ADMIN_USER) + valores)
        conexion.commit()
    respuesta = resumen_compras(conexion)
    conexion.close()
    return jsonify(respuesta), (201 if request.method == 'POST' else 200)


@app.route('/api/compras/<int:id>', methods=['PUT', 'DELETE'])
@requiere_login
def modificar_compra(id):
    conexion = conectar_bd()
    fila = conexion.execute('SELECT * FROM compras WHERE id = ?', (id,)).fetchone()
    if not fila:
        conexion.close()
        return jsonify({"error": "No existe"}), 404
    if fila['envio_id'] is not None:
        conexion.close()
        return jsonify({"error": "Ya se ha enviado y no se puede cambiar"}), 409
    if not session.get('es_admin') and fila['usuario_id'] != session.get('usuario_id'):
        conexion.close()
        return jsonify({"error": "Solo puedes cambiar lo que has apuntado tú"}), 403
    if request.method == 'DELETE':
        conexion.execute('DELETE FROM compras WHERE id = ?', (id,))
    else:
        valores, error = validar_compra(request.get_json(silent=True) or {})
        if error:
            conexion.close()
            return jsonify({"error": error}), 400
        conexion.execute('UPDATE compras SET descripcion = ?, cantidad = ?, proveedor = ?, referencia = ?, precio = ? WHERE id = ?',
                         valores + (id,))
    conexion.commit()
    respuesta = resumen_compras(conexion)
    conexion.close()
    return jsonify(respuesta)


def texto_peticion_rs(articulos, nombre, correo):
    lineas = []
    for n, a in enumerate(articulos, 1):
        ref = f"Ref. RS {a['referencia']}" if a['referencia'] else 'Ref. RS (sin referencia)'
        lineas.append(f"{n}. {ref} | Cantidad: {a['cantidad']} | {a['descripcion']}")
    contacto = f"{nombre}" + (f" <{correo}>" if correo else '')
    return (
        "Buenos días:\n\n"
        "Desde el Servicio de Ingeniería Oceanográfica del Institut de Ciències del Mar (ICM-CSIC) "
        "les solicitamos una cotización de los siguientes artículos:\n\n"
        + "\n".join(lineas) +
        "\n\nLes agradeceríamos que en la oferta indicaran el precio unitario, el plazo de entrega "
        "y los gastos de envío, si los hay.\n\n"
        "Muchas gracias.\n\n"
        f"{contacto}\n"
        "Servicio de Ingeniería Oceanográfica (SIO)\n"
        "Institut de Ciències del Mar (ICM-CSIC)\n"
        "Passeig Marítim de la Barceloneta, 37-49\n"
        "08003 Barcelona\n"
    )


@app.route('/api/compras/enviar', methods=['POST'])
@requiere_login
def enviar_compras():
    """Envia a RS la petició de pressupost dels articles de RS pendents (si arriben al mínim)."""
    if not os.environ.get('SIO_SMTP_HOST'):
        return jsonify({"error": "Envío no configurado en el servidor"}), 503
    conexion = conectar_bd()
    pendientes = [dict(f) for f in conexion.execute('SELECT * FROM compras WHERE envio_id IS NULL ORDER BY fecha, id')]
    articulos = [f for f in pendientes if es_rs(f['proveedor'])]
    total = round(sum((f['precio'] or 0) * f['cantidad'] for f in articulos), 2)
    if not articulos or total < COMPRAS_MINIMO:
        conexion.close()
        return jsonify({"error": "Todavía no se llega al importe mínimo"}), 400
    usuario = conexion.execute('SELECT nombre, email FROM usuarios WHERE id = ?', (session.get('usuario_id'),)).fetchone()
    nombre = (usuario['nombre'] if usuario else None) or session.get('nombre') or ADMIN_USER
    correo = (usuario['email'] if usuario else '') or ''

    mensaje = EmailMessage()
    mensaje['Subject'] = 'Solicitud de cotización - ICM-CSIC (Servicio de Ingeniería Oceanográfica)'
    mensaje['From'] = os.environ.get('SIO_SMTP_FROM', CONTACTO_DESTINO)
    mensaje['To'] = COMPRAS_DESTINO
    copia = [c for c in {correo, CONTACTO_DESTINO} if c]
    if copia:
        mensaje['Cc'] = ', '.join(sorted(copia))
    mensaje['Reply-To'] = correo or CONTACTO_DESTINO
    mensaje.set_content(texto_peticion_rs(articulos, nombre, correo))
    try:
        enviar_correo(mensaje)
    except Exception as e:
        print(f"Error enviando la petición de compras: {e}", flush=True)
        conexion.close()
        return jsonify({"error": "No se ha podido enviar el correo"}), 502

    cursor = conexion.execute('INSERT INTO compras_envios (enviado_por, destinatario, total, articulos) VALUES (?, ?, ?, ?)',
                              (nombre, COMPRAS_DESTINO, total, len(articulos)))
    conexion.executemany('UPDATE compras SET envio_id = ? WHERE id = ?', [(cursor.lastrowid, a['id']) for a in articulos])
    conexion.commit()
    respuesta = resumen_compras(conexion)
    conexion.close()
    return jsonify(respuesta)


if __name__ == '__main__':
    if not login_configurado():
        print("⚠️  Faltan SIO_SECRET_KEY, SIO_ADMIN_USER o SIO_ADMIN_PASSWORD_HASH: la intranet no podrá iniciar sesión")
    print("🚀 Arrancando el motor del SIO en http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=os.environ.get('FLASK_DEBUG') == '1')