from email import message_from_binary_file
from rest_framework import serializers 
from .models import MystromDevice, MystromResult
 
 
class MystromDeviceSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = MystromDevice
        fields = ('id',
                  'name',
                  'ip')
