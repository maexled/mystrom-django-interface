from django.urls import reverse
from django.test import TestCase
from mystrom_rest.models import MystromDevice, MystromResult
from bs4 import BeautifulSoup


class MystromDevicesTestCase(TestCase):
    def setUp(self):
        MystromDevice.objects.create(name="Device 1", ip="192.168.0.205")
        MystromDevice.objects.create(name="Device 2", ip="127.0.0.1")

    def test_create_device(self):
        url = reverse("mystrom_devices")
        response = self.client.post(url, {"name": "test", "ip": "127.0.0.1"})
        self.assertContains(response, "test")
        self.assertContains(response, "127.0.0.1")
        self.assertContains(response, "<td>test</td>")
        self.assertContains(response, "<td>127.0.0.1</td>")
        self.assertEqual(len(MystromDevice.objects.all()), 3)

    def test_create_device_fail_invalid_ip(self):
        url = reverse("mystrom_devices")
        response = self.client.post(url, {"name": "test", "ip": "Not an ip"})
        self.assertContains(
            response, '<div class="invalid-feedback">Not valid IP Address</div>'
        )
        self.assertEqual(len(MystromDevice.objects.all()), 2)

    def test_delete_devices(self):
        url = reverse("mystrom_devices")
        response = self.client.delete(url)
        self.assertNotContains(response, "<tr>")
        self.assertEqual(len(MystromDevice.objects.all()), 0)

    def test_get_create_device_form(self):
        url = reverse("mystrom_devices")
        response = self.client.get(url)
        self.assertContains(response, "Create")
        self.assertContains(response, "<form")
        self.assertContains(response, "</form>")

    def test_update_device(self):
        url = reverse("mystrom_device", args=(1,))
        device = MystromDevice.objects.get(id=1)

        self.assertEqual(device.name, "Device 1")
        response = self.client.post(
            url, {"name": "Not Device 1", "ip": "192.168.0.205"}
        )
        self.assertContains(response, "Not Device 1")

        device = MystromDevice.objects.get(id=1)
        self.assertEqual(device.name, "Not Device 1")

    def test_update_device_fail_invalid_ip(self):
        url = reverse("mystrom_device", args=(1,))
        response = self.client.post(url, {"name": "Not Device 1", "ip": "Not an ip"})
        self.assertContains(
            response, '<div class="invalid-feedback">Not valid IP Address</div>'
        )
        self.assertEqual(len(MystromDevice.objects.all()), 2)

    def test_delete_device(self):
        url = reverse("mystrom_device", args=(1,))
        response = self.client.delete(url)
        self.assertContains(response, "<td>Device 2</td>")
        self.assertNotContains(response, "<td>Device 1</td>")
        self.assertEqual(len(MystromDevice.objects.all()), 1)

    def test_get_update_device_form(self):
        url = reverse("mystrom_device", args=(1,))
        response = self.client.get(url)
        self.assertContains(response, "Edit device")
        self.assertContains(response, "<form")
        self.assertContains(response, "</form>")


class MystromResultsTestCase(TestCase):
    def setUp(self):
        self.device = MystromDevice.objects.create(name="Device 1", ip="192.168.0.205")

    def test_get_results_page(self):
        url = reverse("results")
        response = self.client.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        button = soup.find(id="mystrom-" + str(self.device.id))
        self.assertIsNotNone(button)
