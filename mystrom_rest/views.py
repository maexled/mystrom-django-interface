from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from django.utils import timezone
from dateutil import parser
from datetime import timedelta
from rest_framework.parsers import JSONParser
from rest_framework import status

from django.db import connection

from .models import MystromResult, MystromDevice
from .serializers import MystromDeviceSerializer, MystromResultSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

import logging

logger = logging.getLogger("MyStromRest")


@api_view(["GET", "POST", "DELETE"])
def device_list(request):
    if request.method == "GET":
        devices = MystromDevice.objects.all()

        devices_serializer = MystromDeviceSerializer(devices, many=True)
        return JsonResponse(devices_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == "POST":
        device_data = JSONParser().parse(request)
        device_serializer = MystromDeviceSerializer(data=device_data)
        if device_serializer.is_valid():
            device_serializer.save()

            return JsonResponse(device_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(
            device_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == "DELETE":
        count = MystromDevice.objects.all().delete()
        return JsonResponse(
            {"message": "{} Devices were deleted successfully!".format(count[0])},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET", "PUT", "DELETE"])
def device_detail(request, id):
    device = get_object_or_404(MystromDevice, id=id)

    if request.method == "GET":
        device_serializer = MystromDeviceSerializer(device)
        return JsonResponse(device_serializer.data)

    elif request.method == "PUT":
        device_data = JSONParser().parse(request)
        device_serializer = MystromDeviceSerializer(device, data=device_data)
        if device_serializer.is_valid():
            device_serializer.save()
            return JsonResponse(device_serializer.data)
        return JsonResponse(
            device_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == "DELETE":
        device.delete()
        return JsonResponse(
            {"message": "Device was deleted successfully!"},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET"])
def device_results(request, id):
    # measure time of request
    start_time = timezone.now()
    device = get_object_or_404(MystromDevice, id=id)

    start_param = request.GET.get("start")
    end_param = request.GET.get("end")

    start_param = request.GET.get(
        "start", (timezone.now() - timedelta(days=1)).isoformat()
    )
    end_param = request.GET.get("end", timezone.now().isoformat())

    # Use dateutil parser to handle different formats
    start_param = parser.parse(start_param)
    end_param = parser.parse(end_param)

    # Ensure dates are timezone-aware
    if start_param.tzinfo is None:
        start_param = timezone.make_aware(start_param)
    if end_param.tzinfo is None:
        end_param = timezone.make_aware(end_param)

    logger.debug(f"Request for device {device.id} from {start_param} to {end_param}")

    # Determine interval length based on date range
    interval_length = 5 if (end_param - start_param).days <= 7 else 15

    query_results = """
        SELECT 
            time_bucket('{interval_length} minutes', date) AS interval,
            AVG(ws) AS avg_ws,
            AVG(power) AS avg_power,
            AVG(temperature) AS avg_temperature,
            MIN(date) AS min_date
        FROM 
            {table_name}
        WHERE 
            device_id = %s AND
            date BETWEEN %s AND %s
        GROUP BY 
            interval
        ORDER BY 
            interval;
    """.format(table_name=MystromResult._meta.db_table, interval_length=interval_length)

    query_total_power = """
        WITH interval_data AS (
            SELECT 
                date,
                power,
                device_id
            FROM 
                {table_name}
            WHERE 
                device_id = %s AND 
                date BETWEEN %s AND %s
        ),
        hourly_totals AS (
            SELECT 
                time_bucket('1 hour', date) AS interval,
                AVG(power) AS total_power_per_hour
            FROM 
                interval_data
            GROUP BY 
                interval
        ),
        min_max_dates AS (
            SELECT 
                MIN(date) AS min_date,
                MAX(date) AS max_date
            FROM 
                interval_data
        )
        SELECT 
            SUM(
                CASE 
                    WHEN interval = time_bucket('1 hour', (SELECT min_date FROM min_max_dates)) 
                    THEN total_power_per_hour * (1 - (EXTRACT(epoch FROM age((SELECT min_date FROM min_max_dates), date_trunc('hour', (SELECT min_date FROM min_max_dates)))) / 3600.0))
                    WHEN interval = time_bucket('1 hour', (SELECT max_date FROM min_max_dates)) 
                    THEN total_power_per_hour * (EXTRACT(epoch FROM age(date_trunc('hour', (SELECT max_date FROM min_max_dates)), (SELECT max_date FROM min_max_dates))) / 3600.0)
                    ELSE total_power_per_hour
                END
            ) AS total_power_wh
        FROM 
            hourly_totals;
    """.format(table_name=MystromResult._meta.db_table)

    # Execute the query
    with connection.cursor() as cursor:
        # Execute the interval query
        cursor.execute(query_results, (device.id, start_param, end_param))
        rows_15min = cursor.fetchall()

        cursor.execute(query_total_power, (device.id, start_param, end_param))
        total_power_wh = cursor.fetchone()[0]

        results_15min = [
            {
                "interval": interval,
                "ws": ws,
                "power": power,
                "temperature": temperature,
                "date": date,
            }
            for (interval, ws, power, temperature, date) in rows_15min
        ]

        if request.META.get("HTTP_ACCEPT") == "text/csv":
            result_data = results_15min
        else:
            result_data = {"results": results_15min, "total_power": total_power_wh}

        end_time = timezone.now()
        logging.debug("Request took: " + str(end_time - start_time))

        return Response(result_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_and_save_device_results(request):
    if request.method == "POST":
        devices = MystromDevice.objects.filter(active=True).all()
        results = []
        for device in devices:
            result = device.get_and_save_result()
            results.append(result)
        result_serializer = MystromResultSerializer(results, many=True)
        return JsonResponse(
            result_serializer.data, safe=False, status=status.HTTP_200_OK
        )
