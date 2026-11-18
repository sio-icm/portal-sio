#!/bin/bash
# Copia de seguridad diaria del portal SIO (base de datos + fotos del diario).
# La ejecuta el temporizador sio-copia.timer (ver README, «Copias de seguridad»).
#
# - La base de datos se copia con la función backup de SQLite desde dentro del
#   contenedor: la copia es coherente aunque alguien esté escribiendo.
# - Cada día queda un sio-AAAA-MM-DD.tgz en COPIAS (fuera de datos/) y se
#   borran los de más de DIAS_GUARDAR días.
# - Si existe NEXTCLOUD_CONF (/etc/sio-nextcloud.conf), la copia también se sube
#   al Nextcloud del CSIC (SACO) por WebDAV y allí se guardan las NC_GUARDAR más
#   recientes. Si la subida falla, la copia local queda hecha igualmente.
set -euo pipefail

PORTAL=${PORTAL:-/home/bardaji/sio-portal}
COPIAS=${COPIAS:-/home/bardaji/sio-copias}
DIAS_GUARDAR=${DIAS_GUARDAR:-30}
NEXTCLOUD_CONF=${NEXTCLOUD_CONF:-/etc/sio-nextcloud.conf}
# Dueño de las copias: el usuario que se conecta por SSH para bajarlas a otro ordenador
PROPIETARIO=${PROPIETARIO:-bardaji}
HOY=$(date +%F)
TEMPORAL=copia-en-curso.db

mkdir -p "$COPIAS"
chmod 700 "$COPIAS"
cd "$PORTAL"

# 1. Copia coherente de la base de datos (queda en datos/ un momento)
docker compose exec -T backend python -c "
import sqlite3
origen = sqlite3.connect('/datos/sio_inventario.db')
destino = sqlite3.connect('/datos/$TEMPORAL')
origen.backup(destino)
destino.close()
assert sqlite3.connect('/datos/$TEMPORAL').execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
"

# 2. Empaquetar la copia y las fotos; quitar la copia temporal
tar czf "$COPIAS/sio-$HOY.tgz.parcial" -C "$PORTAL/datos" \
    --transform "s|^$TEMPORAL\$|sio_inventario.db|" "$TEMPORAL" fotos \
    $(cd "$PORTAL/datos" && ls -d equipo documentos 2>/dev/null)
rm -f "$PORTAL/datos/$TEMPORAL"
mv "$COPIAS/sio-$HOY.tgz.parcial" "$COPIAS/sio-$HOY.tgz"
chmod 600 "$COPIAS/sio-$HOY.tgz"
chown "$PROPIETARIO:" "$COPIAS" "$COPIAS/sio-$HOY.tgz"

# 3. Borrar las copias antiguas
find "$COPIAS" -maxdepth 1 -name 'sio-*.tgz' -mtime +"$DIAS_GUARDAR" -delete

echo "Copia hecha: $COPIAS/sio-$HOY.tgz ($(du -h "$COPIAS/sio-$HOY.tgz" | cut -f1))"

# 4. Subirla al Nextcloud (opcional)
[ -f "$NEXTCLOUD_CONF" ] || exit 0
NC_URL=https://saco.csic.es
NC_CARPETA="SIO/Còpies portal SIO"
NC_GUARDAR=30
NC_USUARIO=""
NC_CLAVE=""
# shellcheck source=/dev/null
. "$NEXTCLOUD_CONF"
if [ -z "$NC_USUARIO" ] || [ -z "$NC_CLAVE" ]; then
    echo "AVISO: faltan NC_USUARIO o NC_CLAVE en $NEXTCLOUD_CONF; no se sube al Nextcloud" >&2
    exit 1
fi
codificar() { python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1]))' "$1"; }
DESTINO="$NC_URL/remote.php/dav/files/$(codificar "$NC_USUARIO")/$(codificar "$NC_CARPETA")"
# El usuario y la contraseña van por la entrada estándar: no salen en la lista de procesos
nc_curl() { printf 'user = "%s:%s"\n' "$NC_USUARIO" "$NC_CLAVE" | curl -K - --silent --show-error --fail --max-time 600 "$@"; }

if ! nc_curl -T "$COPIAS/sio-$HOY.tgz" "$DESTINO/sio-$HOY.tgz"; then
    echo "AVISO: no se ha podido subir la copia al Nextcloud ($NC_URL, carpeta «$NC_CARPETA»). La copia local está hecha." >&2
    exit 1
fi
echo "Subida al Nextcloud: $NC_CARPETA/sio-$HOY.tgz"

# En el Nextcloud se guardan las NC_GUARDAR copias más recientes
lista=$(nc_curl -X PROPFIND -H 'Depth: 1' "$DESTINO/" | grep -o 'sio-[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}\.tgz' | sort -u || true)
total=$(printf '%s\n' "$lista" | grep -c . || true)
if [ "$total" -gt "$NC_GUARDAR" ]; then
    printf '%s\n' "$lista" | head -n $((total - NC_GUARDAR)) | while read -r viejo; do
        nc_curl -X DELETE "$DESTINO/$viejo" && echo "Borrada del Nextcloud: $viejo"
    done
fi
