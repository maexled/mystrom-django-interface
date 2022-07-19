from django.db import models
from django.core.validators import RegexValidator

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