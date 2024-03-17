## About the Project

The Django application is designed to allow users to view power usage charts for MyStrom and Shelly3EM devices. The application collects the current power usage data every 60 seconds, which is then used to calculate and present power usage charts to the user.

There are two main views: the Device view and the Result view. Here's what each view looks like:

#### Device View

![Device View](https://user-images.githubusercontent.com/39833217/219866064-89c24f07-c297-46cb-9003-b8dc2c2c39a0.png)

In the Device view, users can add new devices that they want to track. Once added, the device will be listed in the Devices table.

#### Result View

![Result View](https://user-images.githubusercontent.com/39833217/219866092-e4213690-3adf-4afd-a188-a7bbefdfc8fa.png)

In the Result view, users can view power usage charts for their devices. They can select the device they want to view data for, and then choose the date range they want to view data for.


## Prerequisites

* \>= python3.10 [Django Supported Python Versions](https://docs.djangoproject.com/en/5.0/releases/5.0/#python-compatibility)

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

## Environment Variables

Here's a breakdown of all the environment variables that are being used in the Django application:

- `ENGINE_TYPE`: Specifies the type of database engine to use, either `mysql` or `postgresql`.
- `DB_NAME`: Specifies the name of the database to use.
- `DB_USER`: Specifies the username to use when connecting to the database.
- `DB_PASSWORD`: Specifies the password to use when connecting to the database.
- `DB_HOST`: Specifies the host to use when connecting to the database.
- `DB_PORT`: Specifies the port to use when connecting to the database.
- `SECRET_KEY`: Specifies the secret key to use for the Django application.
- `ALLOWED_HOSTS`: Specifies a comma-separated list of hosts that are allowed to access the application.
- `CORS_ORIGIN_ALLOW_ALL`: Specifies whether to allow all cross-origin requests.
- `CORS_ORIGIN_WHITELIST`: Specifies a comma-separated list of whitelisted origins for cross-origin requests.
- `CHART_TYPE`: Specifies the type of chart library to use, either `apexcharts` or `uplot`.
- `TZ`: Specifies the timezone to use for the Django application.

### Chart Types

The `CHART_TYPE` environment variable specifies the type of chart library to use for the Django application. There are two options: `apexcharts` and `uplot`. Here are examples of what each chart type looks like:

#### ApexCharts

![ApexCharts Example](https://user-images.githubusercontent.com/39833217/219865603-48d5e207-5ba7-4d97-b784-579ec487aed4.png)

ApexCharts is a modern charting library that provides a wide range of chart types and features. However, it can have longer loading times when dealing with very large datasets.

#### uPlot

![uPlot Example](https://user-images.githubusercontent.com/39833217/219865544-9721bd75-73cb-40f4-8516-4a4ec52d21c1.png)


uPlot is a lightweight and fast charting library that excels at handling large datasets with many data points. It's an ideal choice for applications that need to render charts with a lot of data, but with a smaller feature set.

## Database migrations
```sh
python manage.py makemigrations
python manage.py migrate
```
   
## Run App
```sh
python manage.py collectstatic
python manage.py runserver
```
Static files are served with WhiteNoise.

## Run with docker
```sh
docker run \
   --name mystrom-interface \
   -p 8000:8000 \
   -e ENGINE_TYPE={mysql/postgresql}
   -e DB_NAME=db-name \
   -e DB_USER=username \
   -e DB_PASSWORD=password \
   -e DB_HOST=host \
   -e DB_PORT=port \
   -e SECRET_KEY=secretKey \
   -e ALLOWED_HOSTS=localhost,mysite.com \
   -e CORS_ORIGIN_ALLOW_ALL=False \
   -e CORS_ORIGIN_WHITELIST=http://localhost:8000,http://mysite.com \
   -e CHART_TYPE={apexcharts/uplot}
   -e TZ=Europe/Berlin \
   ghcr.io/maexled/mystrom-django-interface
```
Make sure to replace the content in `{...}` with your variable of your choice.

## Run with docker-compose and needed containers
```sh
ENGINE_TYPE={mysql/postgresql} DB_HOST=host DB_PORT=port DB_NAME=dbname DB_USER=username DB_PASSWORD=passowrd SECRET_KEY=secretkey ALLOWED_HOSTS=localhost,myhost.com CORS_ORIGIN_ALLOW_ALL=False CORS_ORIGIN_WHITELIST=http://localhost,http://myhost.com CHART_TYPE={apexcharts/uplot} TZ=Europe/Berlin docker compose up
```
Make sure to replace the content in `{...}` with your variable of your choice.

## Configurations
### Important things to know
Database configuraton in `pim/settings.py` under `DATABASES`
