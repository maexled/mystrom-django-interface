from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from .models import MystromDevice, MystromResult


class MystromDeviceTests(APITestCase):
    def test_create_device(self):
        """
        Ensure we can create a new device object.
        """
        url = reverse("rest_device_index")
        data = {"name": "NewDevice", "ip": "192.168.0.196"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MystromDevice.objects.count(), 1)
        self.assertEqual(MystromDevice.objects.get().name, "NewDevice")
        self.assertEqual(MystromDevice.objects.get().ip, "192.168.0.196")

    def test_create_device_fail_invalid_ip(self):
        """
        Ensure we can not create a new device object when ip is invalid.
        """
        url = reverse("rest_device_index")
        data = {"name": "NewDevice", "ip": "notanip"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(MystromDevice.objects.count(), 0)


class MystromResultsTest(APITestCase):
    amount_of_results = 60
    average_power = 0

    def setUp(self):
        device = MystromDevice.objects.create(name="NewDevice", ip="localhost")

        for i in range(self.amount_of_results):
            power = 500
            result = MystromResult(
                device=device,
                power=power,
                ws=power,
                relay=1,
                temperature=25,
                date=timezone.now() + timezone.timedelta(minutes=-1 * i),
            )
            result.save()

        # calulcate average power
        self.average_power = 500
        self.assertEqual(MystromResult.objects.count(), self.amount_of_results)

    def test_get_results_from_device_date_range_no_value(self):
        """
        Ensure we get no result when date range has no results
        """
        start_param = "2023-05-12T22:00:00.835Z"
        end_param = "2023-05-15T22:00:00.835Z"

        url = f"{reverse('rest_device_results', kwargs={'id': 1})}?minimize=false&start={start_param}&end={end_param}"
        response = self.client.get(url, format="json")
        self.assertEqual(len(response.json().get("results")), 0)
