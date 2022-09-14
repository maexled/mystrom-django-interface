from django.db import models
from django.core.validators import RegexValidator

class Shelly3EMDevice(models.Model):

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
        db_table = 'shelly3em_devices'

class Shelly3EMResult(models.Model):

    id = models.AutoField(primary_key=True)

    device = models.ForeignKey(Shelly3EMDevice, on_delete=models.PROTECT)

    total_power = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return "<Result(deivce_id='%s', total_power='%s', date='%s')>" % (
                self.device_id, self.total_power, self.date)

    class Meta:
        db_table = 'shelly3em_results'

class Shelly3EMEmeterResult(models.Model):
    id = models.AutoField(primary_key=True)

    result = models.ForeignKey(Shelly3EMResult, on_delete=models.PROTECT, related_name='emeters')

    emeter_id = models.IntegerField()
    power = models.FloatField()
    pf = models.FloatField()
    current = models.FloatField()
    voltage = models.FloatField()
    total = models.FloatField()
    total_returned = models.FloatField()

    def __repr__(self):
        return "<EmeterResult(device_id='%s', result='%s', emeter_id='%s', power='%s', pf='%s', current='%s', voltage='%s', total='%s', total_returned='%s')>" % (
                self.device_id, self.result, self.emeter_id, self.power, self.pf, self.current, self.voltage, self.total, self.total_returned)

    class Meta:
        db_table = 'shelly3em_emeter_results'