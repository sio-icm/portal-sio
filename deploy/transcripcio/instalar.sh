#!/bin/bash
# Instal·la l'ordinador de transcripció del SIO en aquest PC (Ubuntu/Debian).
#   bash instalar.sh
# Fa:
#  1. Programes del sistema que calen (python3-venv) i Ollama (model d'IA local, per a l'esborrany).
#  2. Un entorn de Python a ~/sio-transcripcio amb Whisper (transcripció) i, si es vol,
#     pyannote (separar qui parla; cal un token gratuït de Hugging Face).
#  3. Baixa els models (uns 7 GB en total) perquè la primera transcripció no hagi d'esperar.
#  4. Desa la configuració a ~/.config/sio-transcripcio/config (només la pot llegir aquest usuari).
#  5. Un temporitzador que cada 10 minuts mira si hi ha gravacions pendents (mentre l'ordinador
#     està encès), amb prioritat baixa per no molestar mentre treballes.
# Es pot tornar a executar: no esborra res i només canvia la configuració que li diguis.
set -euo pipefail

DIR="$HOME/sio-transcripcio"
CONF_DIR="$HOME/.config/sio-transcripcio"
CONF="$CONF_DIR/config"
ORIGEN="$(cd "$(dirname "$0")" && pwd)"
MODEL_LLM="${MODEL_LLM:-qwen2.5:7b}"

echo "== Ordinador de transcripció del SIO =="

# 1. Sistema
if ! python3 -c 'import venv, ensurepip' 2>/dev/null; then
    echo "-> Cal python3-venv (demana la contrasenya de sudo)"
    sudo apt-get update -qq && sudo apt-get install -y python3-venv python3-pip
fi
if ! command -v ffmpeg >/dev/null; then
    echo "-> Cal ffmpeg per llegir els àudios (demana la contrasenya de sudo)"
    sudo apt-get update -qq && sudo apt-get install -y ffmpeg
fi
if ! command -v ollama >/dev/null; then
    echo "-> Instal·lant Ollama (model d'IA local; demana la contrasenya de sudo)"
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 2. Entorn de Python
mkdir -p "$DIR" "$CONF_DIR"
cp "$ORIGEN/transcriure.py" "$DIR/transcriure.py"
[ -d "$DIR/venv" ] || python3 -m venv "$DIR/venv"
PIP="$DIR/venv/bin/pip"
"$PIP" install -q --upgrade pip
echo "-> Instal·lant Whisper"
"$PIP" install -q "faster-whisper==1.1.1" requests  # requests: faster-whisper l'importa però no sempre s'instal·la sol

# 3. Configuració
touch "$CONF"; chmod 600 "$CONF"
valor() { grep -E "^$1=" "$CONF" 2>/dev/null | tail -1 | cut -d= -f2- || true; }
posar() { grep -vE "^$1=" "$CONF" > "$CONF.nou" || true; printf '%s=%s\n' "$1" "$2" >> "$CONF.nou"; mv "$CONF.nou" "$CONF"; chmod 600 "$CONF"; }

[ -n "$(valor URL)" ] || posar URL "https://sio.icm.csic.es"
if [ -z "$(valor CLAU)" ]; then
    echo
    echo "Clau de la intranet: a la intranet, Actes de reunió > Ordinador de transcripció >"
    echo "«Generar clau» (cal ser administrador). Enganxa-la aquí (no es veurà):"
    read -rs CLAU; echo
    posar CLAU "$CLAU"
fi
if [ -z "$(valor HF_TOKEN)" ]; then
    echo
    echo "Separar qui parla (opcional). Cal un token de lectura de Hugging Face i acceptar les"
    echo "condicions de pyannote/speaker-diarization-3.1 i pyannote/segmentation-3.0."
    echo "Enganxa el token (o prem Enter per no separar veus de moment; ho pots fer més endavant):"
    read -rs HF; echo
    [ -n "$HF" ] && posar HF_TOKEN "$HF"
fi
[ -n "$(valor MODEL_LLM)" ] || posar MODEL_LLM "$MODEL_LLM"
[ -n "$(valor IDIOMA_ACTA)" ] || posar IDIOMA_ACTA "ca"

if [ -n "$(valor HF_TOKEN)" ]; then
    echo "-> Instal·lant pyannote (separar veus; uns minuts)"
    "$PIP" install -q torch torchaudio --index-url https://download.pytorch.org/whl/cpu
    "$PIP" install -q "pyannote.audio==3.3.2"
fi

# 4. Models (la primera vegada triga)
echo "-> Baixant el model de transcripció (1,6 GB)"
"$DIR/venv/bin/python" -c "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')"
echo "-> Baixant el model per a l'esborrany de l'acta, $(valor MODEL_LLM) (4,7 GB)"
ollama pull "$(valor MODEL_LLM)"
if [ -n "$(valor HF_TOKEN)" ]; then
    echo "-> Baixant el model per separar veus"
    HF_TOKEN="$(valor HF_TOKEN)" "$DIR/venv/bin/python" -c "
import os
from pyannote.audio import Pipeline
Pipeline.from_pretrained('pyannote/speaker-diarization-3.1', use_auth_token=os.environ['HF_TOKEN'])" \
      || echo "   !! No s'ha pogut baixar: comprova que has acceptat les condicions dels dos models a Hugging Face"
fi

# 5. Temporitzador (systemd d'usuari)
UNITATS="$HOME/.config/systemd/user"
mkdir -p "$UNITATS"
cat > "$UNITATS/sio-transcripcio.service" <<EOF
[Unit]
Description=Transcripció de les reunions del SIO
After=network-online.target

[Service]
Type=oneshot
ExecStart=$DIR/venv/bin/python $DIR/transcriure.py
Nice=15
IOSchedulingClass=idle
TimeoutStartSec=6h
EOF
cat > "$UNITATS/sio-transcripcio.timer" <<EOF
[Unit]
Description=Mira cada 10 minuts si hi ha reunions per transcriure

[Timer]
# OnActiveSec: la primera volta, un minut després d'activar-lo (si no, no arrenca fins a reiniciar)
OnActiveSec=1min
OnBootSec=3min
OnUnitInactiveSec=10min
Persistent=true

[Install]
WantedBy=timers.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now sio-transcripcio.timer

echo
echo "-> Prova de connexió:"
"$DIR/venv/bin/python" "$DIR/transcriure.py" --prova
echo
echo "Fet. Cada 10 minuts (amb l'ordinador encès) es transcriuen les gravacions pendents."
echo "Registre: journalctl --user -u sio-transcripcio -f"
