from rest_framework import serializers 
from .models import MaxCubeDevice, MaxCubeThermostatResult
 
 
class MaxCubeDeviceSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = MaxCubeDevice
        read_only_fields = ('id',)
        fields = ('id',
                  'name',
                  'active',
                  'ip',)

class MaxCubeThermostatResultSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = MaxCubeThermostatResult
        fields = ('name',
                  'room_id',
                  'serial',
                  'actual_temperature',
                  'target_temperature',
                  'date')
