from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from django.utils import timezone
from rest_framework.parsers import JSONParser
from rest_framework import status

from django.db.models import Avg, Sum
from django.db.models.functions import TruncHour

from .models import MystromResult, MystromDevice
from .serializers import MystromDeviceSerializer, MystromResultSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST', 'DELETE'])
def device_list(request):
    if request.method == 'GET':
        devices = MystromDevice.objects.all()

        devices_serializer = MystromDeviceSerializer(devices, many=True)
        return JsonResponse(devices_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':
        device_data = JSONParser().parse(request)
        device_serializer = MystromDeviceSerializer(data=device_data)
        if device_serializer.is_valid():
            device_serializer.save()

            return JsonResponse(device_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(device_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = MystromDevice.objects.all().delete()
        return JsonResponse({'message': '{} Devices were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def device_detail(request, id):
    device = get_object_or_404(MystromDevice, id=id)

    if request.method == 'GET':
        device_serializer = MystromDeviceSerializer(device)
        return JsonResponse(device_serializer.data)

    elif request.method == 'PUT':
        device_data = JSONParser().parse(request)
        device_serializer = MystromDeviceSerializer(device, data=device_data)
        if device_serializer.is_valid():
            device_serializer.save()
            return JsonResponse(device_serializer.data)
        return JsonResponse(device_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        device.delete()
        return JsonResponse({'message': 'Device was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def device_results(request, id):
    device = get_object_or_404(MystromDevice, id=id)

    start_param = request.GET.get('start')
    end_param = request.GET.get('end')

    start_param = request.GET.get(
        'start', timezone.now() + timezone.timedelta(days=-1))
    end_param = request.GET.get('end', timezone.now())

    results = MystromResult.objects.filter(device_id=device, date__range=[
                                           start_param, end_param]).values('ws', 'power', 'relay', 'temperature', 'date').order_by('date')

    average_power = (
        results
        .values('date', 'power')
        .annotate(hour=TruncHour('date'))
        .values('hour')
        .annotate(average_power=Avg('power'))
    )

    total_power = 0

    if average_power.exists():

        # reduce power average based on if first or last hour is not complete
        first_hour = average_power.first()['hour']
        first_hour_results = results.filter(
            date__range=[first_hour, first_hour + timezone.timedelta(hours=1)]).values('date').order_by('date')
        first_hour_percent = (first_hour_results.first()['date'] - first_hour) / timezone.timedelta(hours=1)
        first_hour_power_reduction = average_power.first()['average_power'] * first_hour_percent


        last_hour = average_power.last()['hour']
        last_hour_results = results.filter(
            date__range=[last_hour, last_hour + timezone.timedelta(hours=1)]).values('date').order_by('date')
        last_hour_percent = ((last_hour + timezone.timedelta(hours=1)) - last_hour_results.last()['date']) / timezone.timedelta(hours=1)
        last_hour_power_reduction = average_power.last()['average_power'] * last_hour_percent


        total_power = average_power.aggregate(Sum('average_power'))[
            'average_power__sum'] - first_hour_power_reduction - last_hour_power_reduction

    if request.method == 'GET':
        if request.GET.get('minimize', "false") == "true":
            minimizedList = minimizeResultList(results)
        else:
            minimizedList = results
        result_serializer = MystromResultSerializer(minimizedList, many=True)
        
        if request.META.get('HTTP_ACCEPT') == 'text/csv':
            result_data = result_serializer.data
        else:
            result_data = {'results': result_serializer.data,
                           'total_power': total_power}

        return Response(result_data)

def minimizeResultList(results) -> list:
    resultList = []
    if len(results) == 0:
        return resultList
    skip = 1
    if (len(results) > 10000):
        skip = 20
    elif (len(results) > 5000):
        skip = 10
    elif (len(results) > 1600):
        skip = 5
    elif (len(results) > 500):
        skip = 2

    currentSkip = 0
    currentObj = None
    for result in results.iterator():
        if currentSkip % skip == 0:
            if currentObj != None:
                calculateAverage(currentObj, currentSkip)
                resultList.append(currentObj)
            currentObj = result
            currentSkip = 0
        else:
            currentObj.power += result.power
            currentObj.ws += result.ws
            currentObj.temperature += result.temperature
        currentSkip += 1
    calculateAverage(currentObj, currentSkip)
    resultList.append(currentObj)
    return resultList


def calculateAverage(result, amount) -> MystromResult:
    result.power /= amount
    result.ws /= amount
    result.temperature /= amount
    return result


@api_view(['POST'])
def get_and_save_device_results(request):

    if request.method == 'POST':
        devices = MystromDevice.objects.filter(active=True).all()
        results = []
        for device in devices:
            result = device.get_and_save_result()
            results.append(result)
        result_serializer = MystromResultSerializer(results, many=True)
        return JsonResponse(result_serializer.data, safe=False, status=status.HTTP_200_OK)
