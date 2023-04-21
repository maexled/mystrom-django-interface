from django.shortcuts import render
from django.http.response import JsonResponse
from django.utils import timezone
from rest_framework.parsers import JSONParser 
from rest_framework import status
 
from .models import MystromResult, MystromDevice
from .serializers import MystromDeviceSerializer, MystromResultSerializer
from rest_framework.decorators import api_view

from datetime import datetime

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
    try: 
        device = MystromDevice.objects.get(id=id) 
    except MystromDevice.DoesNotExist: 
        return JsonResponse({'message': 'The device does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
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
    try: 
        device = MystromDevice.objects.get(id=id) 
    except MystromDevice.DoesNotExist: 
        return JsonResponse({'message': 'The device does not exist'}, status=status.HTTP_404_NOT_FOUND) 

    
    start_param = request.GET.get('start')
    end_param = request.GET.get('end')

    if start_param:
        try:
            start_date = datetime.strptime(start_param, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                start_date = datetime.strptime(start_param, '%Y-%m-%d %H:%M')
            except ValueError:
                start_date = datetime.strptime(start_param, '%Y-%m-%d')
        start_date = timezone.make_aware(start_date)
    else:
        start_date = timezone.now() + timezone.timedelta(days=-1)

    if end_param:
        try:
            end_date = datetime.strptime(end_param, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                end_date = datetime.strptime(end_param, '%Y-%m-%d %H:%M')
            except ValueError:
                end_date = datetime.strptime(end_param, '%Y-%m-%d')
        end_date = timezone.make_aware(end_date)
    else:
        end_date = timezone.now()

    results = MystromResult.objects.filter(device_id=device, date__range=[start_date, end_date])


    if request.method == 'GET':
        if request.GET.get('minimize', "true") != "false":
            minimizedList = minimizeResultList(results)
        else:
            minimizedList = results
        result_serializer = MystromResultSerializer(minimizedList, many=True) 

        return JsonResponse(result_serializer.data, safe=False) 

def minimizeResultList(results) -> list:
    resultList = []
    if len(results) == 0:
        return resultList
    skip = 1
    if (len(results) > 10000):
        skip = 20
    elif(len(results) > 5000):
        skip = 10
    elif(len(results) > 1000):
        skip = 5
    elif(len(results) > 500):
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