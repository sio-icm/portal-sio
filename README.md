# Portal del SIO

Web del Servicio de Ingeniería Oceanográfica (SIO) del ICM-CSIC.

- **Frontend:** Vue 3 + Vite, con Vue Router y vue-i18n (catalán, castellano e inglés).
- **Backend:** Flask + SQLite (`backend/`). Sirve el catálogo de instrumentos, los
  proyectos, el login de la intranet y el formulario de contacto.

```
src/                 Frontend (componentes en src/components, rutas en src/router.js)
src/i18n/            Textos de la web: es.js, ca.js, en.js
src/assets/logos/    Logos de la cabecera (uno por idioma)
public/              Archivos que se sirven tal cual (fotos, manuales en PDF...)
backend/app.py       API (Flask)
backend/sio_inventario.db   Base de datos (no está en git)
deploy/              Configuración para el servidor: Nginx (servidor y contenedor) y variables
Dockerfile, docker-compose.yml, backend/Dockerfile   Instalación con Docker
logos/               Logos del SIO en alta resolución
```

## Trabajar en local

Requisitos: Node.js 20.19+ o 22.12+ y Python 3.10+.

```sh
# Frontend
npm install
npm run dev            # http://localhost:5173

# Backend (en otra terminal)
cd backend
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/python app.py # http://127.0.0.1:5000
```

En desarrollo, Vite pasa las peticiones de `/api` al backend (ver `vite.config.js`).
Para probar el login de la intranet o el formulario de contacto en local hay que
definir las mismas variables que en el servidor (ver `deploy/backend.env.example`).

### Textos e idiomas

Todos los textos de la web están en `src/i18n/es.js`, `ca.js` y `en.js`, con las
mismas claves en los tres. Al editarlos, ojo con `{ } @ $ |`, que vue-i18n
interpreta: para escribir una arroba hay que poner `{'@'}`.

Lo que viene de la base de datos (nombres y descripciones de instrumentos y
proyectos) se muestra tal cual, sin traducir.

## Instalar en el servidor (docker03.icm.csic.es)

El portal corre en Docker en el servidor `docker03` (10.100.201.12):

```
Internet / red del centro
        │  80 → 443 (HTTPS)
Nginx del servidor  (/etc/nginx/conf.d/sio.conf, certificado de Informática)
        │  127.0.0.1:8082
Contenedor frontend  (Nginx con la web compilada; /api/ → backend)
        │  red interna de Docker
Contenedor backend   (Flask + gunicorn)  ──  ./datos/sio_inventario.db
```

Solo el Nginx del servidor es accesible desde fuera. Los contenedores escuchan
únicamente dentro del servidor.

En el servidor no hay git: el código se descarga de GitHub (el repositorio es
público) con `curl`.

### 1. Subir los cambios a GitHub (en tu ordenador)

```sh
git push
```

### 2. Descargar el código en una carpeta nueva (en el servidor)

```sh
cd ~ && curl -sL -o portal-sio-codigo.tgz https://github.com/sio-icm/portal-sio/archive/refs/heads/arreglos.tar.gz
mkdir -p ~/sio-portal && tar xzf ~/portal-sio-codigo.tgz -C ~/sio-portal --strip-components=1
rm ~/portal-sio-codigo.tgz
cd ~/sio-portal
```

(Cuando la rama `arreglos` se fusione con `main`, cambiar `arreglos` por `main`
en la dirección.)

La instalación antigua (`~/portal-sio`) no se toca hasta el final.

### 3. Base de datos y usuario del backend

```sh
mkdir -p datos
cp ~/portal-sio/backend/sio_inventario.db datos/
printf 'SIO_UID=%s\nSIO_GID=%s\n' "$(id -u)" "$(id -g)" > .env
```

El backend corre con tu usuario, que es el dueño de `datos/`.

### 4. Variables del backend (contraseña de la intranet, clave de sesión, correo)

```sh
sudo mkdir -p /etc/sio-portal
sudo cp deploy/backend.env.example /etc/sio-portal/backend.env
sudo chmod 600 /etc/sio-portal/backend.env
```

Genera la clave de sesión y el hash de la contraseña de la intranet:

```sh
python3 -c "import secrets; print(secrets.token_hex(32))"
sudo docker compose run --rm --no-deps backend python -c "from werkzeug.security import generate_password_hash as g; print(g('LA_CONTRASEÑA'))"
```

y rellena el archivo con `sudo nano /etc/sio-portal/backend.env`. El hash va
**entre comillas simples** (`SIO_ADMIN_PASSWORD_HASH='scrypt:...'`).

### 5. Arrancar los contenedores

```sh
sudo docker compose up -d --build
sudo docker compose ps
```

Comprobar desde el propio servidor, antes de cambiar nada en Nginx:

```sh
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8082/            # 200
curl -s http://127.0.0.1:8082/api/proyectos | head -c 200                     # JSON
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8082/servicios      # 200
```

Si algo falla: `sudo docker compose logs backend` o `sudo docker compose logs frontend`.

### 6. Pasar el Nginx del servidor a la instalación nueva

```sh
sudo cp /etc/nginx/conf.d/sio.conf /etc/nginx/sio.conf.antes-de-docker
```

- **Si todavía no hay certificado:** `sudo cp deploy/nginx-sio-sin-https.conf /etc/nginx/conf.d/sio.conf`
- **Con el certificado** (ver el paso 7): `sudo cp deploy/nginx-sio.conf /etc/nginx/conf.d/sio.conf`

```sh
sudo nginx -t && sudo systemctl reload nginx
```

Para volver atrás:
`sudo cp /etc/nginx/sio.conf.antes-de-docker /etc/nginx/conf.d/sio.conf && sudo systemctl reload nginx`.

Si la web da error 502 y en `/var/log/nginx/error.log` aparece *Permission denied*
al conectar con 127.0.0.1:8082, es SELinux: `sudo setsebool -P httpd_can_network_connect 1`.

### 7. Certificado HTTPS

Informática envía un `.crt` y un `.key`. La clave (`.key`) es secreta: no se
reenvía, no se pega en ningún sitio y no se sube al repositorio.

```sh
sudo mkdir -p /etc/pki/nginx/private
sudo cp sio.icm.csic.es.crt /etc/pki/nginx/sio.icm.csic.es.crt
sudo cp sio.icm.csic.es.key /etc/pki/nginx/private/sio.icm.csic.es.key
sudo chmod 600 /etc/pki/nginx/private/sio.icm.csic.es.key
sudo restorecon -Rv /etc/pki/nginx           # SELinux
sudo firewall-cmd --permanent --add-service=https && sudo firewall-cmd --reload   # si usa firewalld
```

Si el `.crt` no incluye la cadena intermedia, hay que añadirla al final del mismo
archivo (pedirla a Informática). Después, aplicar `deploy/nginx-sio.conf` (paso 6),
poner `SIO_COOKIE_SEGURA=1` en `/etc/sio-portal/backend.env` y reiniciar:
`sudo docker compose up -d`.

### 8. Comprobar

- `https://sio.icm.csic.es/` carga la portada y `http://` redirige a `https://`.
- `/proyectos` muestra los proyectos y recargar en cualquier sección no da 404.
- Se puede entrar en la intranet con el usuario configurado.
- Desde otro ordenador, los puertos 8000, 8081 y 8082 no responden.

### 9. Retirar la instalación antigua

Cuando todo funcione:

```sh
cd ~/portal-sio && sudo docker compose down        # contenedores antiguos (puertos 8000 y 8081)
pkill -u "$USER" -f "portal-sio/backend/app.py"    # backend antiguo arrancado a mano (puerto 5000)
```

La carpeta `~/portal-sio` se puede guardar un tiempo como copia.

## Actualizar la web

1. En tu ordenador: `git push`.
2. En el servidor:

```sh
cd ~ && curl -sL -o portal-sio-codigo.tgz https://github.com/sio-icm/portal-sio/archive/refs/heads/arreglos.tar.gz
cd ~/sio-portal && find . -mindepth 1 -maxdepth 1 ! -name datos ! -name .env -exec rm -rf {} + && tar xzf ~/portal-sio-codigo.tgz --strip-components=1
rm ~/portal-sio-codigo.tgz
sudo docker compose up -d --build
sudo docker image prune -f
```

- La segunda línea vacía `~/sio-portal` **excepto `datos/` y `.env`** y descomprime
  la versión nueva, para que no se queden archivos que ya se han borrado del
  repositorio. La base de datos y `/etc/sio-portal/backend.env` no se tocan.
- `docker image prune -f` borra las imágenes antiguas que deja cada
  reconstrucción, para que no se llene el disco.

## Copias de seguridad

Toda la información editable (instrumentos y proyectos) está en
`~/sio-portal/datos/sio_inventario.db`. Para copiarla sin parar el backend:

```sh
cd ~/sio-portal
sudo docker compose exec backend python -c "import sqlite3; sqlite3.connect('/datos/sio_inventario.db').backup(sqlite3.connect('/datos/copia-$(date +%F).db'))"
```

La copia queda en `datos/copia-AAAA-MM-DD.db`.

## Usuarios de la intranet y diario de actividad

- El usuario de `/etc/sio-portal/backend.env` (`SIO_ADMIN_USER`) es el
  **administrador del servidor**. Desde la intranet, en «Usuaris», crea los
  usuarios personales de cada persona del equipo (y puede hacer administradores
  a otros).
- Cada persona cambia su contraseña en «El meu compte».
- El **diari d'activitat** guarda notas (fecha, proyecto o «sense projecte»,
  tipo, texto). Cada uno edita las suyas; los administradores, todas.
- El **informe semestral** sale de esas notas: se elige el periodo y se imprime
  o se guarda en PDF.
- Las tablas `usuarios` y `notas` se crean solas en la base de datos al arrancar
  el backend.

## Cambiar la contraseña de la intranet del administrador del servidor

```sh
cd ~/sio-portal
sudo docker compose run --rm --no-deps backend python -c "from werkzeug.security import generate_password_hash as g; print(g('NUEVA_CONTRASEÑA'))"
sudo nano /etc/sio-portal/backend.env      # SIO_ADMIN_PASSWORD_HASH='...'
sudo docker compose up -d
```

## Notas del servidor docker03

- Tiene 3,5 GB de RAM. El 19-10-2026 se congeló por falta de memoria: el servidor
  de VS Code (Remote Explorer) ocupa unos 2 GB. Conviene cerrar la ventana remota
  al terminar y no instalar extensiones en el servidor.
- Tiene 2 GB de swap en `/swapfile` (activada en `/etc/fstab`, etiqueta SELinux
  `swapfile_t` registrada con `semanage fcontext`).
- Nginx del servidor y los contenedores arrancan solos al reiniciar
  (`systemctl enable nginx`, `restart: unless-stopped`).
