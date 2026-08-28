# My Portfolio

This Django project uses the same codebase for local development and production.
Its behavior is selected with `DJANGO_ENV` and all environment-specific values
come from environment variables.

## Local development

The repository already includes a Git-ignored `.env` configured for local use.

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Development uses SQLite, enables Django debug pages, and serves uploaded media
through Django. To create a fresh configuration, copy `.env.example` to `.env`.

## Production

Set the values from `.env.production.example` in the hosting provider's secret or
environment-variable panel. At minimum, replace these values:

- `DJANGO_SECRET_KEY`: a unique, random secret that is never committed
- `DJANGO_ALLOWED_HOSTS`: comma-separated hostnames without `https://`
- `DJANGO_CSRF_TRUSTED_ORIGINS`: comma-separated full HTTPS origins
- `DATABASE_URL`: a persistent PostgreSQL connection URL

Production always disables `DEBUG`, enables secure cookies and HTTPS redirect,
uses PostgreSQL through `DATABASE_URL`, serves collected static assets with
WhiteNoise, and runs behind Gunicorn.

The initial HSTS duration is one hour. Increase it gradually only after HTTPS is
working reliably; enable subdomains/preload only when every subdomain supports
HTTPS permanently.

Build/release commands for a conventional Python host are:

```text
python -m pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn my_portfolio.wsgi:application --bind 0.0.0.0:$PORT
```

The included `Procfile` provides equivalent release/web processes. The included
`Dockerfile` is a portable production option:

```text
docker build -t my-portfolio .
docker run --env-file .env.production -p 8000:8000 my-portfolio
```

Do not store production uploads only inside an ephemeral container. Mount a
persistent volume at `DJANGO_MEDIA_ROOT` or configure an object-storage backend
before relying on admin-uploaded images and resume files.

## Environment behavior

| Setting | Development | Production |
| --- | --- | --- |
| Debug pages | Enabled by default | Always disabled |
| Database | Local SQLite | `DATABASE_URL` (PostgreSQL recommended) |
| Static files | Django development server | WhiteNoise + `collectstatic` |
| Uploaded media | Served locally by Django | Persistent volume/object storage required |
| HTTPS security | Off | Secure cookies and redirect enabled |
