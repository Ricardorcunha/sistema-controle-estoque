# ============================================================
# Dockerfile — Multi-stage build
# Stage 1: build do React (Node)
# Stage 2: imagem final Django (Python slim)
#
# Multi-stage build: o Node.js é usado apenas para compilar o
# frontend. A imagem final não carrega o Node, mantendo-a menor.
# ============================================================

# ── Stage 1: Build do React ───────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copia dependências e instala (aproveita cache do Docker)
COPY frontend/package*.json ./
RUN npm ci --silent

# Copia o restante do código e compila
COPY frontend/ ./
RUN npm run build
# O output fica em /frontend/dist


# ── Stage 2: Aplicação Django ─────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="Ricardo <ricardorcunha96@gmail.com>"
LABEL description="Sistema de Controle de Estoque — Django + React"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# Dependências do sistema (psycopg2 precisa de libpq-dev)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements/ requirements/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements/production.txt

# Copia código da aplicação
COPY . .

# Copia o build do React para a pasta de static files do Django
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

# Coleta todos os static files em STATIC_ROOT (WhiteNoise vai servir)
RUN python manage.py collectstatic --noinput

# Usuário não-root por segurança
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Em produção: gunicorn no lugar do runserver
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
