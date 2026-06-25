#!/usr/bin/env sh
set -e

python manage.py migrate --noinput
python manage.py seed_initial_data
python manage.py create_admin_from_env
python manage.py collectstatic --noinput

exec gunicorn cashflow_project.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers "${GUNICORN_WORKERS:-3}"
