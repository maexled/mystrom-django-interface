from rest_framework import serializers
from .models import Shelly3EMDevice, Shelly3EMEmeterResult, Shelly3EMResult


class Shelly3EMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelly3EMDevice
        read_only_fields = ("id",)
        fields = (
            "id",
            "name",
            "active",
            "ip",
        )


class Shelly3EMEmeterResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelly3EMEmeterResult
        fields = (
            "emeter_id",
            "power",
            "pf",
            "current",
            "voltage",
            "total",
            "total_returned",
        )


class Shelly3EMResultSerializer(serializers.ModelSerializer):
    emeters = Shelly3EMEmeterResultSerializer(many=True)

    class Meta:
        model = Shelly3EMResult
        fields = ("emeters", "total_power", "date")
