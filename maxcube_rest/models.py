from django.db import models
from django.core.validators import RegexValidator

class MaxCubeDevice(models.Model):

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
        db_table = 'maxcubes'

class MaxCubeThermostatResult(models.Model):

    id = models.AutoField(primary_key=True)

    device = models.ForeignKey(MaxCubeDevice, on_delete=models.PROTECT)

    name = models.CharField(max_length=16)
    room_id = models.IntegerField()
    serial = models.CharField(max_length=16)

    actual_temperature = models.FloatField()
    target_temperature = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

  # Lets us print out a user object conveniently.
    def __repr__(self):
        return "<Result(deivce_id='%s', name='%s', room_id='%s', serial='%s', actual_temperature='%s', target_temperature='%s', date='%s')>" % (
                self.device_id, self.name, self.room_id, self.serial, self.actual_temperature, self.target_temperature, self.date)

    class Meta:
        db_table = 'maxcube_thermostat_results'