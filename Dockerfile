FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt ./


RUN apk add gcc musl-dev mariadb-connector-c-dev libpq-dev


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
CMD python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind=0.0.0.0:8000 --timeout 300 --workers=3 --threads=3 --max-requests 5 --max-requests-jitter 2 pim.wsgi:application
EXPOSE 8000/tcp