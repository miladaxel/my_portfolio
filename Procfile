release: python manage.py migrate --noinput
web: python manage.py collectstatic --noinput && gunicorn my_portfolio.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --timeout ${GUNICORN_TIMEOUT:-60} --access-logfile - --error-logfile -
