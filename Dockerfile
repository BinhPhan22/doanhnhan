FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_DEBUG=0
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libjpeg62-turbo zlib1g postgresql-client \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# collectstatic cần SECRET_KEY tạm thời khi build
RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput \
    && useradd -r -u 1000 app && mkdir -p /data/media /data/private_media && chown -R app /data /app
USER app

ENV MEDIA_ROOT=/data/media PRIVATE_MEDIA_ROOT=/data/private_media
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3} --timeout 60 --access-logfile -"]
