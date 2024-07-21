from rest_framework import serializers
from .models import MystromDevice, MystromResult


class MystromDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MystromDevice
        read_only_fields = ("id",)
        fields = (
            "id",
            "name",
            "active",
            "ip",
        )


class MystromResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MystromResult
        fields = ("power", "ws", "relay", "temperature", "date")
