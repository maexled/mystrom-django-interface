FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py makemigrations && python manage.py migrate
CMD ["gunicorn", "--bind=0.0.0.0:8000", "pim.wsgi:application"]
EXPOSE 8000/tcp