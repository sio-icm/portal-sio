#!/bin/bash
# Copia de seguridad diaria del portal SIO (base de datos + fotos del diario).
# La ejecuta el temporizador sio-copia.timer (ver README, «Copias de seguridad»).
#
# - La base de datos se copia con la función backup de SQLite desde dentro del
#   contenedor: la copia es coherente aunque alguien esté escribiendo.
# - Cada día queda un sio-AAAA-MM-DD.tgz en COPIAS (fuera de datos/) y se
#   borran los de más de DIAS_GUARDAR días.
set -euo pipefail

PORTAL=${PORTAL:-/home/bardaji/sio-portal}
COPIAS=${COPIAS:-/home/bardaji/sio-copias}
DIAS_GUARDAR=${DIAS_GUARDAR:-30}
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
