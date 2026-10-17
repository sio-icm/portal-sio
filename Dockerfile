# Frontend del portal SIO: compila la web con Vite y la sirve con Nginx.
# Nginx también pasa /api/ al contenedor del backend (ver deploy/nginx-contenedor.conf).

# --- Etapa 1: compilar la web ---
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# --- Etapa 2: servir la web compilada ---
FROM nginx:1.28-alpine
COPY deploy/nginx-contenedor.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
