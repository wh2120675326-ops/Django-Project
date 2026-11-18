#!/usr/bin/env bash
set -o errexit
exec gunicorn campus_skillswap.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --access-logfile - --error-logfile -
