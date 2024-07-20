# Stage 1: Build stage
FROM python:3.12-alpine AS builder

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc musl-dev mariadb-connector-c-dev libpq-dev

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
FROM python:3.12-alpine

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=builder /app /app

RUN apk add --no-cache mariadb-connector-c libpq

COPY . .


CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind=0.0.0.0:8000 --timeout 300 --workers=3 --threads=3 --max-requests 20 --max-requests-jitter 5 pim.wsgi:application"]

EXPOSE 8000/tcp
