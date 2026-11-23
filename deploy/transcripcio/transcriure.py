#!/usr/bin/env python3
"""Ordinador de transcripció del SIO.

Pregunta a la intranet si hi ha gravacions de reunions pendents, les baixa, les transcriu
(Whisper), separa qui parla (pyannote, si hi ha token de Hugging Face), dona nom a les veus
a partir de les presentacions de l'inici i en fa un esborrany d'acta amb un model local
(Ollama). Tot es fa en aquest ordinador: no s'envia res a serveis de fora.

El llança cada 10 minuts el temporitzador sio-transcripcio.timer (vegeu instalar.sh).
Configuració: ~/.config/sio-transcripcio/config (URL, CLAU, HF_TOKEN, ...).
Ús manual:  transcriure.py          → processa el que hi hagi pendent
            transcriure.py --prova  → només comprova la connexió i diu què hi ha pendent
"""
import fcntl
import json
import os
import re
import socket
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

CONFIG = os.path.expanduser('~/.config/sio-transcripcio/config')
BLOQUEIG = os.path.expanduser('~/.cache/sio-transcripcio.lock')


def llegir_config():
    conf = {'URL': 'https://sio.icm.csic.es', 'CLAU': '', 'HF_TOKEN': '', 'MODEL_WHISPER': 'large-v3-turbo',
            'MODEL_LLM': 'qwen2.5:7b', 'OLLAMA': 'http://127.0.0.1:11434', 'IDIOMA_ACTA': 'ca',
            'FILS': str(max(1, (os.cpu_count() or 4) - 2))}
    if os.path.exists(CONFIG):
        for linia in open(CONFIG, encoding='utf-8'):
            linia = linia.strip()
            if linia and not linia.startswith('#') and '=' in linia:
                k, v = linia.split('=', 1)
                conf[k.strip()] = v.strip().strip('"').strip("'")
    return conf


CONF = llegir_config()


def log(*a):
    print(time.strftime('%Y-%m-%d %H:%M:%S'), *a, flush=True)


# ---------- Intranet ----------
def peticio(metode, ruta, dades=None, desar_a=None, temps=120):
    cos = json.dumps(dades).encode() if dades is not None else None
    req = urllib.request.Request(CONF['URL'].rstrip('/') + ruta, data=cos, method=metode, headers={
        'Authorization': 'Bearer ' + CONF['CLAU'], 'X-Maquina': socket.gethostname(),
        'Content-Type': 'application/json', 'User-Agent': 'sio-transcripcio/1'})
    with urllib.request.urlopen(req, timeout=temps) as r:
        if desar_a:
            with open(desar_a, 'wb') as f:
                while True:
                    bloc = r.read(1 << 20)
                    if not bloc:
                        break
                    f.write(bloc)
            return None
        return json.loads(r.read() or b'null')


ESTAT = {'aid': None, 'progres': ''}


def avisar(aid, progres, comencar=False):
    ESTAT.update(aid=aid, progres=progres)
    try:
        peticio('POST', f'/api/transcripcion/{aid}/estado', {'progreso': progres, 'empezar': comencar})
    except Exception as e:  # no és greu
        log('no es pot avisar del progrés:', e)


def batec():
    """Cada 2 minuts torna a dir per on va: si l'ordinador s'apaga, la intranet ho nota i la
    gravació es torna a oferir a la propera vegada."""
    while True:
        time.sleep(120)
        if ESTAT['aid']:
            try:
                peticio('POST', f"/api/transcripcion/{ESTAT['aid']}/estado", {'progreso': ESTAT['progres']})
            except Exception:
                pass


# ---------- Ollama (model local per a noms i esborrany) ----------
def ollama(missatges, json_format=False, context=8192):
    cos = {'model': CONF['MODEL_LLM'], 'messages': missatges, 'stream': False, 'keep_alive': '2m',
           'options': {'temperature': 0.2, 'num_ctx': context, 'num_thread': int(CONF['FILS'])}}
    if json_format:
        cos['format'] = 'json'
    req = urllib.request.Request(CONF['OLLAMA'].rstrip('/') + '/api/chat', data=json.dumps(cos).encode(),
                                 headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=3 * 3600) as r:
        return json.loads(r.read())['message']['content']


def ollama_disponible():
    try:
        with urllib.request.urlopen(CONF['OLLAMA'].rstrip('/') + '/api/tags', timeout=5) as r:
            models = [m['name'] for m in json.loads(r.read()).get('models', [])]
        return any(m == CONF['MODEL_LLM'] or m.split(':')[0] == CONF['MODEL_LLM'] for m in models)
    except Exception:
        return False


IDIOMES = {'ca': 'català', 'es': 'castellà', 'en': 'anglès'}


def text_amb_veus(segments, noms, fins=None):
    linies, anterior = [], None
    for s in segments:
        if fins is not None and s['inicio'] > fins:
            break
        qui = noms.get(s['hablante'], s['hablante']) or '?'
        if qui != anterior:
            linies.append(f"\n[{qui}] {s['texto']}")
            anterior = qui
        else:
            linies[-1] += ' ' + s['texto']
    return ''.join(linies).strip()


def noms_de_les_veus(segments, acta):
    """Les persones es presenten a l'inici: el model relaciona cada veu amb un nom."""
    veus = sorted({s['hablante'] for s in segments if s['hablante']})
    if len(veus) < 1:
        return {}
    inici = text_amb_veus(segments, {}, fins=360)
    assistents = ', '.join(acta['asistentes'] + ([acta['otros_asistentes']] if acta['otros_asistentes'] else []))
    prompt = (
        "Aquí tens l'inici de la transcripció d'una reunió. Cada intervenció porta l'etiqueta de la veu "
        f"({', '.join(veus)}). Al començament els assistents es presenten (p. ex. «Sóc la Nina, del SIO»).\n"
        f"Assistents previstos: {assistents or 'desconeguts'}.\n\n"
        "Digues quin nom correspon a cada veu, NOMÉS si es dedueix clarament de les presentacions "
        "(si no, posa \"\"). Fes servir el nom complet de la llista d'assistents si hi coincideix. "
        'Respon només amb JSON, per exemple {"Veu 1": "Nina Hoareau", "Veu 2": ""}.\n\n' + inici)
    try:
        resposta = json.loads(ollama([{'role': 'user', 'content': prompt}], json_format=True))
        return {v: str(resposta.get(v) or '').strip() for v in veus if isinstance(resposta, dict)}
    except Exception as e:
        log('no s\'han pogut deduir els noms:', e)
        return {}


def esborrany_acta(segments, noms, acta):
    idioma = IDIOMES.get(CONF['IDIOMA_ACTA'], 'català')
    text = text_amb_veus(segments, noms)
    context = min(32768, max(8192, int(len(text) / 3) + 4096))
    assistents = ', '.join(acta['asistentes'] + ([acta['otros_asistentes']] if acta['otros_asistentes'] else []))
    prompt = (
        f"Ets el secretari d'una reunió del Servei d'Enginyeria Oceanogràfica (SIO) de l'ICM-CSIC. "
        f"A partir de la transcripció, escriu l'esborrany de l'acta en {idioma}.\n"
        f"Reunió: {acta['titulo']} ({acta['fecha']}){' · projecte ' + acta['proyecto'] if acta['proyecto'] else ''}.\n"
        f"Assistents: {assistents or 'vegeu la transcripció'}.\n\n"
        "Format: HTML senzill, sense <html> ni <body>, amb aquestes seccions:\n"
        "<h2>Ordre del dia</h2> (llista <ol> dels temes tractats)\n"
        "<h2>Desenvolupament</h2> (resum de cada tema en paràgrafs <p> curts: què es va dir i qui ho va proposar)\n"
        "<h2>Acords</h2> (llista <ul>)\n"
        "<h2>Tasques</h2> (llista <ul>: tasca — responsable — termini, si es diu)\n"
        "Sigues fidel a la transcripció: no t'inventis res; si alguna cosa no s'entén, indica-ho amb [?]. "
        "No copiïs la transcripció literalment: resumeix.\n\nTRANSCRIPCIÓ:\n" + text)
    html = ollama([{'role': 'user', 'content': prompt}], context=context)
    html = re.sub(r'^```(?:html)?\s*|\s*```\s*$', '', html.strip())
    # Tasques en format de llista per omplir la taula de tasques de l'acta
    tasques = []
    try:
        r = json.loads(ollama([{'role': 'user', 'content': (
            "Extreu les tasques d'aquesta acta. Respon només amb JSON: "
            '{"tareas": [{"texto": "...", "responsable": "...", "fecha": "AAAA-MM-DD o buit"}]}. '
            "Si no n'hi ha, llista buida.\n\n" + html)}], json_format=True))
        for t in (r.get('tareas') or [])[:50]:
            if isinstance(t, dict) and str(t.get('texto', '')).strip():
                data = str(t.get('fecha') or '')
                tasques.append({'texto': str(t['texto']).strip()[:500], 'responsable': str(t.get('responsable') or '').strip()[:100],
                                'fecha': data if re.fullmatch(r'\d{4}-\d{2}-\d{2}', data) else '', 'hecha': False})
    except Exception as e:
        log('no s\'han pogut extreure les tasques:', e)
    return json.dumps({'html': html, 'tareas': tasques}, ensure_ascii=False)


# ---------- Transcripció ----------
def transcriure(p, fitxer):
    from faster_whisper import WhisperModel, decode_audio
    aid = p['id']
    audio = decode_audio(fitxer, sampling_rate=16000)
    durada = len(audio) / 16000 or 1
    avisar(aid, 'transcrivint 0 %')
    model = WhisperModel(CONF['MODEL_WHISPER'], device='cpu', compute_type='int8', cpu_threads=int(CONF['FILS']))
    # Els noms dels assistents ajuden Whisper a escriure'ls bé
    pista = 'Reunió del SIO. ' + ', '.join(p['acta']['asistentes'])
    segs, info = model.transcribe(audio, beam_size=5, vad_filter=True, multilingual=True, initial_prompt=pista,
                                  condition_on_previous_text=False)
    segments, darrer = [], 0
    for s in segs:
        segments.append({'inicio': s.start, 'fin': s.end, 'hablante': '', 'texto': s.text.strip()})
        if time.time() - darrer > 60:
            avisar(aid, f'transcrivint {min(99, int(100 * s.end / durada))} %')
            darrer = time.time()
    del model
    return audio, segments, info.language


def separar_veus(aid, audio, segments):
    if not CONF['HF_TOKEN']:
        return segments
    avisar(aid, 'separant les veus')
    import torch
    from pyannote.audio import Pipeline
    torch.set_num_threads(int(CONF['FILS']))
    pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization-3.1', use_auth_token=CONF['HF_TOKEN'])
    diar = pipeline({'waveform': torch.from_numpy(audio).unsqueeze(0), 'sample_rate': 16000})
    torns = [(t.start, t.end, qui) for t, _, qui in diar.itertracks(yield_label=True)]
    etiquetes = {}
    for _, _, qui in sorted(torns):
        etiquetes.setdefault(qui, f'Veu {len(etiquetes) + 1}')
    for s in segments:
        sol = {}
        for a, b, qui in torns:
            encavalcament = min(b, s['fin']) - max(a, s['inicio'])
            if encavalcament > 0:
                sol[qui] = sol.get(qui, 0) + encavalcament
        if sol:
            s['hablante'] = etiquetes[max(sol, key=sol.get)]
    return segments


def processar(p):
    aid = p['id']
    log(f"gravació {aid}: «{p['acta']['titulo']}» ({p['duracion'] // 60} min)")
    avisar(aid, 'baixant l\'àudio', comencar=True)
    with tempfile.TemporaryDirectory(prefix='sio-') as tmp:
        fitxer = os.path.join(tmp, f"audio.{p['formato'] or 'webm'}")
        peticio('GET', f'/api/transcripcion/{aid}/audio', desar_a=fitxer, temps=1800)
        inici = time.time()
        audio, segments, idioma = transcriure(p, fitxer)
        log(f'  transcrit en {int(time.time() - inici) // 60} min ({len(segments)} fragments, idioma {idioma})')
        try:
            segments = separar_veus(aid, audio, segments)
        except Exception as e:
            log('  no s\'han pogut separar les veus:', e)
        del audio
    noms, esborrany = {}, ''
    if segments and ollama_disponible():
        if any(s['hablante'] for s in segments):
            avisar(aid, 'posant nom a les veus')
            noms = noms_de_les_veus(segments, p['acta'])
        avisar(aid, "escrivint l'esborrany de l'acta")
        try:
            esborrany = esborrany_acta(segments, noms, p['acta'])
        except Exception as e:
            log("  no s'ha pogut fer l'esborrany:", e)
    elif segments:
        log(f"  Ollama o el model {CONF['MODEL_LLM']} no hi són: només transcripció")
    peticio('POST', f'/api/transcripcion/{aid}/resultado',
            {'segmentos': segments, 'hablantes': noms, 'idioma': idioma, 'borrador': esborrany}, temps=600)
    log(f'  fet en {int(time.time() - inici) // 60} min')


def main():
    if not CONF['CLAU']:
        sys.exit(f'Falta la CLAU a {CONFIG}')
    os.makedirs(os.path.dirname(BLOQUEIG), exist_ok=True)
    bloqueig = open(BLOQUEIG, 'w')
    try:
        fcntl.flock(bloqueig, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log('ja hi ha una transcripció en marxa')
        return
    try:
        pendents = peticio('GET', '/api/transcripcion/pendientes')
    except urllib.error.HTTPError as e:
        sys.exit('La intranet no accepta la clau (genereu-ne una de nova a Actes de reunió)' if e.code == 401 else f'Error de la intranet: {e}')
    except Exception as e:
        log('sense connexió amb la intranet:', e)
        return
    if '--prova' in sys.argv:
        print(f"Connexió correcta amb {CONF['URL']}. Gravacions pendents: {len(pendents)}")
        print('Model local per a l\'acta:', 'disponible' if ollama_disponible() else f"NO disponible ({CONF['MODEL_LLM']})")
        print('Separar veus:', 'sí' if CONF['HF_TOKEN'] else 'no (sense HF_TOKEN)')
        return
    threading.Thread(target=batec, daemon=True).start()
    for p in pendents:
        try:
            processar(p)
        except Exception as e:
            log(f"  error amb la gravació {p['id']}:", e)
            try:
                peticio('POST', f"/api/transcripcion/{p['id']}/resultado", {'error': str(e)[:900]})
            except Exception:
                pass
        ESTAT['aid'] = None


if __name__ == '__main__':
    main()
