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
3. Install needed python libraries
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
   -e TZ=Europe/Berlin \
   ghcr.io/maexled/mystrom-django-interface
```

## Configurations
### Important things to know
Database configuraton in `pim/settings.py` under `DATABASES`
