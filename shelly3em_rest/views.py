from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
 
from .models import Shelly3EMDevice, Shelly3EMResult, Shelly3EMEmeterResult
from .serializers import Shelly3EMDeviceSerializer, Shelly3EMResultSerializer, Shelly3EMEmeterResultSerializer
from rest_framework.decorators import api_view

import datetime

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
    try: 
        device = Shelly3EMDevice.objects.get(id=id) 
    except Shelly3EMDevice.DoesNotExist: 
        return JsonResponse({'message': 'The device does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
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
    try: 
        device = Shelly3EMDevice.objects.get(id=id) 
    except Shelly3EMDevice.DoesNotExist: 
        return JsonResponse({'message': 'The device does not exist'}, status=status.HTTP_404_NOT_FOUND) 
    
    start_date=request.GET.get('start', datetime.datetime.now() + datetime.timedelta(days=-1))
    end_date=request.GET.get('end', datetime.datetime.now())

    results = Shelly3EMResult.objects.filter(device_id=device, date__range=[start_date,end_date])

    if request.method == 'GET':
        result_serializer = Shelly3EMResultSerializer(results, many=True) 

        return JsonResponse(result_serializer.data, safe=False) 