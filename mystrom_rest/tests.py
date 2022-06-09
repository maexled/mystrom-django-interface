from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import MystromDevice

class MystromDeviceTests(APITestCase):
    def test_create_device(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('rest_device_index')
        data = {'name': 'NewDevice', 'ip': '192.168.0.196'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MystromDevice.objects.count(), 1)
        self.assertEqual(MystromDevice.objects.get().name, 'NewDevice')
        self.assertEqual(MystromDevice.objects.get().ip, '192.168.0.196')

    def test_create_device_fail_invalid_ip(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('rest_device_index')
        data = {'name': 'NewDevice', 'ip': 'notanip'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(MystromDevice.objects.count(), 0)