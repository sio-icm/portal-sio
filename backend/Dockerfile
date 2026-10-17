# Backend del portal SIO: Flask servido con gunicorn.
# La base de datos no va dentro de la imagen: se monta en /datos (ver docker-compose.yml).
FROM python:3.12-slim

# HOME=/tmp: el contenedor corre con el usuario del servidor (sin carpeta
# personal dentro) y gunicorn necesita una carpeta escribible para su control
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

EXPOSE 8000
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "app:app"]
