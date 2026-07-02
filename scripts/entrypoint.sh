#!/bin/sh
# ============================================================
# entrypoint.sh — Script de entrada do container Docker
# ============================================================
# Garante que:
# 1. O banco de dados esteja disponível
# 2. As migrations estejam aplicadas
# 3. Os arquivos estáticos estejam coletados (em prod)
# 4. O servidor seja iniciado

set -e  # Interrompe se qualquer comando falhar

echo "============================================================"
echo "Sistema de Controle de Estoque — Iniciando..."
echo "============================================================"

echo ">>> Aguardando banco de dados..."
python manage.py wait_for_db

echo ">>> Aplicando migrations..."
python manage.py migrate --noinput

echo ">>> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo ">>> Iniciando servidor..."
# Em desenvolvimento: runserver
# Em produção: gunicorn (configurado via variável de ambiente)
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.production" ]; then
    exec gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 3 \
        --timeout 120 \
        --access-logfile - \
        --error-logfile -
else
    exec python manage.py runserver 0.0.0.0:8000
fi
