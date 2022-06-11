FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./


RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc default-libmysqlclient-dev


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
CMD python manage.py makemigrations && python manage.py migrate && gunicorn --bind=0.0.0.0:8000 pim.wsgi:application
EXPOSE 8000/tcp