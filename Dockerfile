FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt ./


RUN apk add gcc musl-dev mariadb-connector-c-dev


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
CMD python manage.py makemigrations && python manage.py migrate && gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers=3 --threads=3 pim.wsgi:application
EXPOSE 8000/tcp