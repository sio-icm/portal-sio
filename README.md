# Portal del SIO

Web del Servicio de Ingeniería Oceanográfica (SIO) del ICM-CSIC.

- **Frontend:** Vue 3 + Vite, con Vue Router y vue-i18n (catalán, castellano e inglés).
- **Backend:** Flask + SQLite (`backend/`). Sirve el catálogo de instrumentos, los
  proyectos, el login de la intranet, el formulario de contacto y las solicitudes
  de servicios (Pelagia, tanque, instrumentos...).

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

Informática instala el certificado en `/etc/httpd/certs/`: `sio.icm.csic.es.pem`
(certificado + cadena GEANT/HARICA) y `sio.icm.csic.es.key`. La clave es secreta:
no se copia, no se pega en ningún sitio y no se sube al repositorio.
El certificado de noviembre de 2026 **caduca el 22-05-2027**.

```sh
# Comprobar: nombre, fechas, cadena (2 o más) y que la clave corresponde
sudo openssl x509 -in /etc/httpd/certs/sio.icm.csic.es.pem -noout -subject -dates
sudo grep -c "BEGIN CERTIFICATE" /etc/httpd/certs/sio.icm.csic.es.pem
sudo restorecon -Rv /etc/httpd/certs         # SELinux: que Nginx pueda leerlos

# Nginx con HTTPS (copia de la configuración anterior antes)
sudo cp /etc/nginx/conf.d/sio.conf /etc/nginx/sio.conf.antes-de-https
sudo cp ~/sio-portal/deploy/nginx-sio.conf /etc/nginx/conf.d/sio.conf
sudo nginx -t && sudo systemctl reload nginx
```

docker03 no tiene cortafuegos propio (ni firewalld ni nftables); el 443 lo abre
Informática en el de la red. Después, poner `SIO_COOKIE_SEGURA=1` en
`/etc/sio-portal/backend.env` y, en `~/sio-portal`, `sudo docker compose up -d`.

Si algo falla: `sudo cp /etc/nginx/sio.conf.antes-de-https /etc/nginx/conf.d/sio.conf && sudo systemctl reload nginx`.
Cuando renueven el certificado en la misma carpeta: `sudo systemctl reload nginx`.

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

Toda la información editable está en `~/sio-portal/datos/`: la base de datos
`sio_inventario.db` (instrumentos, proyectos, usuarios y notas del diario) y la
carpeta `fotos/` (fotos del diario). Para copiar la base de datos sin parar el
backend:

```sh
cd ~/sio-portal
sudo docker compose exec backend python -c "import sqlite3; sqlite3.connect('/datos/sio_inventario.db').backup(sqlite3.connect('/datos/copia-$(date +%F).db'))"
```

La copia queda en `datos/copia-AAAA-MM-DD.db`. Para tener una copia completa
fuera del servidor, guarda también la carpeta de fotos, por ejemplo:
`tar czf ~/sio-datos-$(date +%F).tgz -C ~/sio-portal datos`.

### Copia automática cada noche

`deploy/copia-seguridad.sh` hace una copia coherente de la base de datos (sin
parar la web), la empaqueta con las fotos en `~/sio-copias/sio-AAAA-MM-DD.tgz`
y borra las de más de 30 días. La lanza un temporizador de systemd a las 3:00
(si el servidor estaba apagado, al arrancar). Instalación, una sola vez:

```sh
cd ~/sio-portal
sudo install -m 755 deploy/copia-seguridad.sh /usr/local/bin/sio-copia-seguridad
sudo cp deploy/sio-copia.service deploy/sio-copia.timer /etc/systemd/system/
sudo restorecon -v /usr/local/bin/sio-copia-seguridad /etc/systemd/system/sio-copia.*
sudo systemctl daemon-reload && sudo systemctl enable --now sio-copia.timer
sudo systemctl start sio-copia.service && ls -lh ~/sio-copias   # primera copia, para probar
```

- Ver cuándo toca la siguiente: `systemctl list-timers sio-copia.timer`
- Ver si ha fallado: `journalctl -u sio-copia.service -n 20`
- Restaurar: `tar xzf ~/sio-copias/sio-AAAA-MM-DD.tgz -C /tmp/restaurar`, parar el
  backend, copiar `sio_inventario.db` y `fotos/` a `~/sio-portal/datos/` y arrancarlo.
- Las copias están en el mismo disco: protegen de errores y borrados, no de que
  se estropee el servidor. De vez en cuando, bájate la última a tu ordenador:
  `scp docker03.icm.csic.es:sio-copias/sio-$(date +%F).tgz ~/`

## Solicitudes de servicios

Los formularios de la Pelagia, el tanque de pruebas, el préstamo de
instrumentos, el análisis de salinidad, los fondeos, el prototipado y la
propuesta de I+D+I **se envían desde la propia web** (`/api/solicitud`): ya no
abren Outlook ni el programa de correo de quien los rellena.

- Llegan a `sio@icm.csic.es` con el asunto `[Web SIO] …`, enviados por el mismo
  servidor y remitente que el formulario de contacto (`SIO_SMTP_*` en
  `/etc/sio-portal/backend.env`). **«Responder» contesta al solicitante**
  (va en `Reply-To`).
- La solicitud de la Pelagia lleva obligatoriamente el Plan de Campaña firmado
  adjunto (PDF o Word, hasta 10 MB).
- Se piden nombre y correo; el navegador los recuerda para la siguiente vez.
- Límite: 10 solicitudes por hora desde la misma IP. Si el envío falla, la web
  muestra el error y la dirección sio@icm.csic.es como alternativa.
- No se guardan en la base de datos: solo se envía el correo.

## Usuarios de la intranet y diario de actividad

- El usuario de `/etc/sio-portal/backend.env` (`SIO_ADMIN_USER`) es el
  **administrador del servidor**. Desde la intranet, en «Usuaris», crea los
  usuarios personales de cada persona del equipo (y puede hacer administradores
  a otros).
- Cada persona cambia su contraseña en «El meu compte», y allí también pone su
  correo (el administrador lo puede poner en «Usuaris»).
- **«Has oblidat l'usuari o la contrasenya?»** (pantalla de acceso): con el
  usuario o el correo, la web envía un enlace que vale una hora y una sola vez.
  Los correos salen por `smtp.icm.csic.es` con el remitente `web-sio@docker03…`:
  nunca en nombre de sio@icm.csic.es. Sin correo configurado, un administrador
  pone una contraseña provisional en «Usuaris → 🔑 Contrasenya».
- El **diari d'activitat** guarda notas (fecha, proyecto o «sense projecte»,
  tipo, texto). Cada uno edita las suyas; los administradores, todas.
- Cada nota puede llevar **hasta 12 fotos**; el servidor las reduce a 1600 px en
  WebP y las guarda en `datos/fotos/`.
- Las notas marcadas como **públicas** solo salen en la web (página `/diario`)
  cuando un administrador las aprueba con «Publicar a la web». Si el autor las
  edita después, vuelven a revisión.
- El **informe semestral** sale de esas notas y del calendari d'equip
  (campañas, formación, reuniones con nota y uso de la Pelagia, el tanque y los
  préstamos; nunca teletrabajo, vacaciones ni bajas): se elige el periodo, se
  quita con la ✕ lo que no interese y se imprime o se guarda en PDF.
- Las tablas `usuarios` y `notas` se crean solas en la base de datos al arrancar
  el backend.

## Memoria anual (página pública /memoria)

Se rellena sola con el diario de actividad y el calendari d'equip
(`/api/memoria?anio=AAAA`), con selector de año:

- Cifras: actividades registradas, proyectos con actividad, días de campaña,
  días con la Pelagia, días de uso del tanque, préstamos de instrumentos y horas
  de soporte (notas sin proyecto con «Temps dedicat»), y actividad por tipo.
- «Actividad destacada»: las notas **públicas y aprobadas** del año (como /diario).
- Nunca salen nombres, notas internas, teletrabajo, vacaciones ni bajas.
- El PDF de la memoria completa se añade en `pdfsMemoria` de
  `src/components/MemoriaAnual.vue` (archivo dentro de `public/`).

## Calendari d'equip

- Cada persona apunta sus días de teletrabajo, campaña, vacaciones, baja,
  formación o reuniones, y reserva la **Pelagia**, el **tanque de pruebas** o un
  **instrumento** (también préstamos a gente de fuera). Cada uno cambia lo suyo;
  los administradores, todo.
- La pantalla principal de la intranet muestra un resumen (Hoy / Semana / Mes).
  «✓ Vist» lo pliega hasta el día siguiente o hasta que salga un aviso nuevo
  (se recuerda en cada navegador).
- **Avisos**: menos personas en el centro que el mínimo (por defecto 3; solo
  cuentan las marcadas como «Plantilla» en «Usuaris»), el mismo recurso
  reservado dos veces y la Pelagia reservada cuando el patrón (por defecto
  `brian`) no está; una persona con dos compromisos fuera a la vez (p. ej. una
  campaña y un congreso), el responsable de una reserva ausente esos días y un
  instrumento reservado que está en mantenimiento. Fines de semana y festivos no
  cuentan. La pantalla principal mira las **próximas 12 semanas** y agrupa los
  avisos por semana («Aquesta setmana», «Setmana del … · d'aquí a N setmanes»).
- Los **festivos de Barcelona** de 2026 y 2027 se cargan la primera vez; los
  administradores los cambian en «Configuració» (los locales de 2027 están
  pendientes de confirmar cuando el Ayuntamiento los publique).
- Las páginas públicas de la Pelagia, los tanques y los instrumentos marcan en
  azul (o rojo) los días reservados, sin nombres ni motivos.
- Tablas: `calendario`, `reservas`, `festius`, `ajustes` (se crean solas).

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
