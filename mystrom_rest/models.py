from django.db import models, transaction
from django.core.validators import RegexValidator
import requests
import json

class MystromDevice(models.Model):

    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=16)
    active = models.BooleanField(default=True)
    ip = models.CharField(max_length=16, validators=[
            RegexValidator(
                regex='^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$',
                message='Not valid IP Address',
            ),
        ])

    def __repr__(self):
        return "<Device(id='%s', name='%s', ip='%s')>" % (
                self.id, self.name, self.ip)
    
    @transaction.atomic
    def get_and_save_result(self):
        try:
            response = requests.get(f'http://{self.ip}/report')
        except requests.exceptions.ConnectionError as e:
            print(f'Device {self.name} with ip address {self.ip} seems to be not reachable.')
            return
        except requests.exceptions.Timeout as e:
            print(f'Request to device {self.name} with ip address {self.ip} timed out.')
            return
        except requests.exceptions.RequestException as e:
            print(f'Request to device {self.name} with ip address {self.ip} failed.')
            return

        try:
            response = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            print(f'Request to device {self.name} with ip address {self.ip} returns invalid JSON response.')
            return

        result = MystromResult(device=self, power=response["power"], ws=response["Ws"], relay=1 if response["relay"] else 0, temperature=response["temperature"])
        result.save()
        return result

    class Meta:
        db_table = 'devices'

class MystromResult(models.Model):

    id = models.AutoField(primary_key=True)

    device = models.ForeignKey(MystromDevice, on_delete=models.PROTECT)

    power = models.FloatField()
    ws = models.FloatField()
    relay = models.IntegerField()
    temperature = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return "<Result(deivce_id='%s', power='%s', ws='%s', relay='%s', temperature='%s', date='%s')>" % (
                self.device_id, self.power, self.ws, self.relay, self.temperature, self.date)

    class Meta:
        db_table = 'results'