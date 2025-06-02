from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Shelly3EMDevice
from .serializers import Shelly3EMDeviceSerializer


class ShellyDeviceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("shelly_rest_device_index")
        self.device_data = {"name": "Test Device", "ip": "192.168.0.74", "active": True}
        self.device = Shelly3EMDevice.objects.create(
            name="Test Device", ip="192.168.0.74", active=True
        )

    def test_get_device_list(self):
        response = self.client.get(self.url)
        devices = Shelly3EMDevice.objects.all()
        serializer = Shelly3EMDeviceSerializer(devices, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), serializer.data)

    def test_create_device_invalid_data(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
