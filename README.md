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
deploy/              Plantillas para el servidor: Nginx, servicio systemd y variables
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

## Instalar en el servidor

Requisitos: Node.js, `python3-venv` y Nginx. Se supone que el repositorio está en
`/opt/portal-sio`; si está en otro sitio, cambiar la ruta en los pasos y plantillas.

1. **Código y frontend**

   ```sh
   sudo git clone https://github.com/sio-icm/portal-sio.git /opt/portal-sio
   cd /opt/portal-sio
   npm ci
   npm run build          # genera dist/
   ```

2. **Backend**

   ```sh
   cd /opt/portal-sio/backend
   python3 -m venv venv
   venv/bin/python -m pip install -r requirements.txt
   ```

   Copiar la base de datos `sio_inventario.db` a `backend/`. El usuario que ejecute
   el backend debe poder escribir en ese archivo y en la carpeta `backend/`.

3. **Variables del backend** (contraseña de la intranet, clave de sesión, correo)

   ```sh
   sudo mkdir -p /etc/sio-portal
   sudo cp deploy/backend.env.example /etc/sio-portal/backend.env
   sudo chmod 600 /etc/sio-portal/backend.env
   sudo nano /etc/sio-portal/backend.env   # rellenar siguiendo los comentarios
   ```

   Sin `SIO_SECRET_KEY`, `SIO_ADMIN_USER` y `SIO_ADMIN_PASSWORD_HASH` no se puede
   entrar en la intranet; sin `SIO_SMTP_HOST`, el formulario de contacto avisa de
   que no puede enviar y ofrece escribir a sio@icm.csic.es.

4. **Servicio del backend**

   Editar `deploy/sio-backend.service` (ruta y usuario) y:

   ```sh
   sudo cp deploy/sio-backend.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now sio-backend
   systemctl status sio-backend
   ```

5. **Nginx y HTTPS**

   Partir de `deploy/nginx-portal-sio.conf`: poner como `root` la carpeta
   `/opt/portal-sio/dist` y las rutas del certificado que proporcione Informática.

   ```sh
   sudo cp deploy/nginx-portal-sio.conf /etc/nginx/sites-available/portal-sio
   sudo ln -s /etc/nginx/sites-available/portal-sio /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```

   El puerto 5000 no se abre fuera del servidor: Nginx pasa `/api/` al backend.

6. **Comprobar**

   - `https://sio.icm.csic.es/` carga la portada.
   - `https://sio.icm.csic.es/proyectos` muestra los proyectos (el backend responde).
   - Recargar en cualquier sección no da error 404.
   - Se puede entrar en la intranet con el usuario configurado.

## Actualizar la web

```sh
cd /opt/portal-sio
git pull
npm ci && npm run build
backend/venv/bin/python -m pip install -r backend/requirements.txt
sudo systemctl restart sio-backend
```

No hace falta recargar Nginx salvo que cambie su configuración.

## Copias de seguridad

Toda la información editable (instrumentos y proyectos) está en
`backend/sio_inventario.db`. Para copiarla sin parar el backend:

```sh
cd /opt/portal-sio/backend
venv/bin/python -c "import sqlite3,sys; sqlite3.connect('sio_inventario.db').backup(sqlite3.connect(sys.argv[1]))" /ruta/copias/sio_inventario-$(date +%F).db
```

## Cambiar la contraseña de la intranet

Generar un hash nuevo, ponerlo en `SIO_ADMIN_PASSWORD_HASH` de
`/etc/sio-portal/backend.env` y reiniciar con `sudo systemctl restart sio-backend`:

```sh
backend/venv/bin/python -c "from werkzeug.security import generate_password_hash as g; print(g('NUEVA_CONTRASEÑA'))"
```
