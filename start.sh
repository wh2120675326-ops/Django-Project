#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# The PPT build command installs dependencies; initialize Django here.
python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Start only after static collection and database migrations succeed.
exec gunicorn campus_skillswap.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --access-logfile - --error-logfile -
