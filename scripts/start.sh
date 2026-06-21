#!/bin/sh
set -e

python manage.py collectstatic --noinput
exec gunicorn kiim_shop.wsgi:application --bind 0.0.0.0:${PORT:-8000}
