FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_ENV=production

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup --system django \
    && adduser --system --ingroup django django \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R django:django /app

USER django

EXPOSE 8000

CMD ["sh", "-c", "python manage.py collectstatic --noinput && if [ \"${RUN_MIGRATIONS:-true}\" = \"true\" ]; then python manage.py migrate --noinput; fi && exec gunicorn my_portfolio.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --timeout ${GUNICORN_TIMEOUT:-60} --access-logfile - --error-logfile -"]
