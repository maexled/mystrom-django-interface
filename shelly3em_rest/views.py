from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from django.utils import timezone
from rest_framework.parsers import JSONParser
from rest_framework import status

from django.db.models import Avg, Sum, Case, When, FloatField
from django.db.models.functions import TruncHour

from .models import Shelly3EMDevice, Shelly3EMResult
from .serializers import Shelly3EMDeviceSerializer, Shelly3EMResultSerializer
from rest_framework.decorators import api_view


@api_view(['GET', 'POST', 'DELETE'])
def device_list(request):
    if request.method == 'GET':
        devices = Shelly3EMDevice.objects.all()

        devices_serializer = Shelly3EMDeviceSerializer(devices, many=True)
        return JsonResponse(devices_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':
        device_data = JSONParser().parse(request)
        device_serializer = Shelly3EMDeviceSerializer(data=device_data)
        if device_serializer.is_valid():
            device_serializer.save()

            return JsonResponse(device_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(device_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = Shelly3EMDevice.objects.all().delete()
        return JsonResponse({'message': '{} Devices were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def device_detail(request, id):
    device = get_object_or_404(Shelly3EMDevice, id=id)

    if request.method == 'GET':
        device_serializer = Shelly3EMDeviceSerializer(device)
        return JsonResponse(device_serializer.data)

    elif request.method == 'PUT':
        device_data = JSONParser().parse(request)
        device_serializer = Shelly3EMDeviceSerializer(device, data=device_data)
        if device_serializer.is_valid():
            device_serializer.save()
            return JsonResponse(device_serializer.data)
        return JsonResponse(device_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        device.delete()
        return JsonResponse({'message': 'Device was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def device_results(request, id):
    device = get_object_or_404(Shelly3EMDevice, id=id)

    start_param = request.GET.get(
        'start', timezone.now() + timezone.timedelta(days=-1))
    end_param = request.GET.get('end', timezone.now())

    results = Shelly3EMResult.objects.filter(
        device_id=device, date__range=[start_param, end_param]).prefetch_related('emeters')

    average_power = (
        results
        .annotate(hour=TruncHour('date'))
        .values('hour')
        .annotate(average_power=Avg('total_power'))
        .annotate(average_power_returned=Avg(Case(
            When(total_power__gt=0, then=0),
            default='total_power',
            output_field=FloatField(),
        )))
    )

    total_power = 0    
    total_returned_power = 0
    
    if average_power.exists():

        # reduce power average based on if first or last hour is not complete
        first_hour = average_power.first()['hour']
        first_hour_results = results.filter(
            date__range=[first_hour, first_hour + timezone.timedelta(hours=1)]).values('date').order_by('date')
        first_hour_percent = (first_hour_results.first()['date'] - first_hour) / timezone.timedelta(hours=1)
        first_hour_power_reduction = average_power.first()['average_power'] * first_hour_percent
        first_hour_power_returned_reduction = average_power.first()['average_power_returned'] * first_hour_percent


        last_hour = average_power.last()['hour']
        last_hour_results = results.filter(
            date__range=[last_hour, last_hour + timezone.timedelta(hours=1)]).values('date').order_by('date')
        last_hour_percent = ((last_hour + timezone.timedelta(hours=1)) - last_hour_results.last()['date']) / timezone.timedelta(hours=1)
        last_hour_power_reduction = average_power.last()['average_power'] * last_hour_percent
        last_hour_power_returned_reduction = average_power.last()['average_power_returned'] * last_hour_percent


        total_power = average_power.aggregate(Sum('average_power'))[
            'average_power__sum'] - first_hour_power_reduction - last_hour_power_reduction
        total_returned_power = average_power.aggregate(Sum('average_power_returned'))[
            'average_power_returned__sum'] - first_hour_power_returned_reduction - last_hour_power_returned_reduction

    if request.method == 'GET':
        result_serializer = Shelly3EMResultSerializer(results, many=True)
        result_data = {'results': result_serializer.data,
                       'total_power': total_power,
                       'total_returned_power': total_returned_power, }
        return JsonResponse(result_data, safe=False)


@api_view(['POST'])
def get_and_save_device_results(request):

    if request.method == 'POST':
        devices = Shelly3EMDevice.objects.filter(active=True).all()
        results = []
        for device in devices:
            result = device.get_and_save_result()
            results.append(result)
        result_serializer = Shelly3EMResultSerializer(results, many=True)

        return JsonResponse(result_serializer.data, safe=False, status=status.HTTP_200_OK)
