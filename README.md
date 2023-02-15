## About the Project
The project is designed to manage mystrom devices in an easy interface.

## Prerequisites

* \>= python3.8

## Installation

1. Clone the repo
```sh
git clone https://github.com/maexled/mystrom-django-interface.git
cd mystrom-django-interface/
```
2. Install needed python libraries
```sh
pip install -r requirements.txt 
```

## Database migrations
```sh
python manage.py makemigrations
python manage.py migrate
```
   
## Run App
```sh
python manage.py runserver
```

## Run with docker
```sh
docker run \
   --name mystrom-interface \
   -p 8000:8000 \
   -e DB_NAME=db-name \
   -e DB_USER=username \
   -e DB_PASSWORD=password \
   -e DB_HOST=host \
   -e DB_PORT=port \
   -e SECRET_KEY=secretKey \
   -e ALLOWED_HOSTS=localhost,mysite.com \
   -e CORS_ORIGIN_ALLOW_ALL=False \
   -e CORS_ORIGIN_WHITELIST=http://localhost:8000,http://mysite.com \
   -e TZ=Europe/Berlin \
   ghcr.io/maexled/mystrom-django-interface
```
Make sure that the static files are not deployed yet. For this look the next section

## Run with docker-compose and needed containers
```sh
DB_HOST=host DB_PORT=port DB_NAME=dbname DB_USER=username DB_PASSWORD=passowrd SECRET_KEY=secretkey ALLOWED_HOSTS=localhost,myhost.com CORS_ORIGIN_ALLOW_ALL=False CORS_ORIGIN_WHITELIST=http://localhost,http://myhost.com TZ=Europe/Berlin docker compose up
```

## Configurations
### Important things to know
Database configuraton in `pim/settings.py` under `DATABASES`
