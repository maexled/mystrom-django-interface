from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
 
from .models import MystromResult, MystromDevice
from .serializers import MystromDeviceSerializer, MystromResultSerializer
from rest_framework.decorators import api_view

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
    results = MystromResult.objects.filter(device_id=device.id)

    if request.method == 'GET': 
        result_serializer = MystromResultSerializer(results, many=True) 
        return JsonResponse(result_serializer.data, safe=False) 
    