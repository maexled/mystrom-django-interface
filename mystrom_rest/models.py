from django.db import models

class MystromDevice(models.Model):

    id = models.IntegerField(primary_key=True)

    name = models.CharField(max_length=16)
    ip = models.CharField(max_length=16)

    def __repr__(self):
        return "<Device(id='%s', name='%s', ip='%s')>" % (
                self.id, self.name, self.ip)

    class Meta:
        db_table = 'devices'

class MystromResult(models.Model):

    id = models.IntegerField(primary_key=True)

    device_id = models.ForeignKey(MystromDevice, on_delete=models.PROTECT)

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