from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from django.utils import timezone
from dateutil import parser
from datetime import timedelta
from rest_framework.parsers import JSONParser
from rest_framework import status

from django.db import connection

from .models import Shelly3EMDevice, Shelly3EMResult, Shelly3EMEmeterResult
from .serializers import Shelly3EMDeviceSerializer, Shelly3EMResultSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

import logging

logger = logging.getLogger("Shelly3EMRest")


@api_view(["GET", "POST", "DELETE"])
def device_list(request):
    if request.method == "GET":
        devices = Shelly3EMDevice.objects.all()

        devices_serializer = Shelly3EMDeviceSerializer(devices, many=True)
        return JsonResponse(devices_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == "POST":
        device_data = JSONParser().parse(request)
        device_serializer = Shelly3EMDeviceSerializer(data=device_data)
        if device_serializer.is_valid():
            device_serializer.save()

            return JsonResponse(device_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(
            device_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == "DELETE":
        count = Shelly3EMDevice.objects.all().delete()
        return JsonResponse(
            {"message": "{} Devices were deleted successfully!".format(count[0])},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET", "PUT", "DELETE"])
def device_detail(request, id):
    device = get_object_or_404(Shelly3EMDevice, id=id)

    if request.method == "GET":
        device_serializer = Shelly3EMDeviceSerializer(device)
        return JsonResponse(device_serializer.data)

    elif request.method == "PUT":
        device_data = JSONParser().parse(request)
        device_serializer = Shelly3EMDeviceSerializer(device, data=device_data)
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
    device = get_object_or_404(Shelly3EMDevice, id=id)

    start_param = request.GET.get("start")
    end_param = request.GET.get("end")

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
            AVG(total_power) AS avg_total_power,
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
    """.format(
        table_name=Shelly3EMResult._meta.db_table, interval_length=interval_length
    )

    query_emeter_results = """
        SELECT 
            time_bucket('{interval_length} minutes', r.date) AS interval,
            er.emeter_id,
            AVG(er.power) AS avg_power,
            AVG(er.pf) AS avg_pf,
            AVG(er.current) AS avg_current,
            AVG(er.voltage) AS avg_voltage,
            AVG(er.total) AS avg_total,
            AVG(er.total_returned) AS avg_total_returned
        FROM 
            {result_table_name} AS r
        JOIN
            {emeter_result_table_name} AS er
        ON 
            r.device_id = er.device_id AND r.date = er.date
        WHERE 
            r.device_id = %s AND
            r.date BETWEEN %s AND %s
        GROUP BY 
            interval, er.emeter_id
        ORDER BY 
            interval, er.emeter_id;
    """.format(
        result_table_name=Shelly3EMResult._meta.db_table,
        emeter_result_table_name=Shelly3EMEmeterResult._meta.db_table,
        interval_length=interval_length,
    )

    query_total_power = """
        WITH interval_data AS (
            SELECT 
                date,
                total_power,
                LEAST(total_power, 0) AS total_power_returned,
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
                AVG(total_power) AS total_power_per_hour,
                AVG(total_power_returned) AS total_power_returned_per_hour
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
            ) AS total_power_wh,
            SUM(
                CASE
                    WHEN interval = time_bucket('1 hour', (SELECT min_date FROM min_max_dates))
                    THEN total_power_returned_per_hour * (1 - (EXTRACT(epoch FROM age((SELECT min_date FROM min_max_dates), date_trunc('hour', (SELECT min_date FROM min_max_dates)))) / 3600.0))
                    WHEN interval = time_bucket('1 hour', (SELECT max_date FROM min_max_dates))
                    THEN total_power_returned_per_hour * (EXTRACT(epoch FROM age(date_trunc('hour', (SELECT max_date FROM min_max_dates)), (SELECT max_date FROM min_max_dates))) / 3600.0)
                    ELSE total_power_returned_per_hour
                END
            ) AS total_power_returned_wh
        FROM 
            hourly_totals;
    """.format(table_name=Shelly3EMResult._meta.db_table)

    with connection.cursor() as cursor:
        params = [device.id, start_param, end_param]
        cursor.execute(query_results, params)
        rows_15min = cursor.fetchall()

        primary_results = [
            {
                "interval": interval,
                "total_power": total_power,
                "date": date,
            }
            for (interval, total_power, date) in rows_15min
        ]

        # Create a dictionary to store emeter results by interval
        emeter_results_by_interval = {}

        cursor.execute(query_emeter_results, params)
        emeter_rows = cursor.fetchall()

        for row in emeter_rows:
            (
                interval,
                emeter_id,
                avg_power,
                avg_pf,
                avg_current,
                avg_voltage,
                avg_total,
                avg_total_returned,
            ) = row
            if interval not in emeter_results_by_interval:
                emeter_results_by_interval[interval] = []
            emeter_results_by_interval[interval].append(
                {
                    "emeter_id": emeter_id,
                    "power": avg_power,
                    "pf": avg_pf,
                    "current": avg_current,
                    "voltage": avg_voltage,
                    "total": avg_total,
                    "total_returned": avg_total_returned,
                }
            )

        # Combine primary results with emeter results
        results_15min = []
        for result in primary_results:
            interval = result["interval"]
            result["emeters"] = emeter_results_by_interval.get(interval, [])
            results_15min.append(result)

        cursor.execute(query_total_power, (device.id, start_param, end_param))
        total_power, total_power_returned = cursor.fetchone()

        if request.META.get("HTTP_ACCEPT") == "text/csv":
            result_data = results_15min
        else:
            result_data = {
                "results": results_15min,
                "total_power": total_power,
                "total_returned_power": total_power_returned,
            }

        return Response(result_data)


@api_view(["POST"])
def get_and_save_device_results(request):
    if request.method == "POST":
        devices = Shelly3EMDevice.objects.filter(active=True).all()
        results = []
        for device in devices:
            result = device.get_and_save_result()
            results.append(result)
        result_serializer = Shelly3EMResultSerializer(results, many=True)

        return JsonResponse(
            result_serializer.data, safe=False, status=status.HTTP_200_OK
        )
