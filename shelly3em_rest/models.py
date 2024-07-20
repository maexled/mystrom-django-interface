from django.db import models, transaction
from cpkmodel import CPkModel
from compositefk.fields import CompositeForeignKey
from django.core.validators import RegexValidator
from django.utils import timezone
import requests
import json

import logging

logger = logging.getLogger("Shelly3EM Models")


class Shelly3EMDevice(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=16)
    active = models.BooleanField(default=True)
    ip = models.CharField(
        max_length=16,
        validators=[
            RegexValidator(
                regex="^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$",
                message="Not valid IP Address",
            ),
        ],
    )

    def __repr__(self):
        return "<Device(id='%s', name='%s', ip='%s')>" % (self.id, self.name, self.ip)

    @transaction.atomic
    def get_and_save_result(self):
        try:
            response = requests.get(f"http://{self.ip}/status")
        except requests.exceptions.ConnectionError as e:
            print(
                f"Device {self.name} with ip address {self.ip} seems to be not reachable."
            )
            return
        except requests.exceptions.Timeout as e:
            print(f"Request to device {self.name} with ip address {self.ip} timed out.")
            return
        except requests.exceptions.RequestException as e:
            print(f"Request to device {self.name} with ip address {self.ip} failed.")
            return

        try:
            response = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            print(
                f"Request to device {self.name} with ip address {self.ip} returns invalid JSON response."
            )
            return

        result = Shelly3EMResult(
            device=self, date=timezone.now(), total_power=response["total_power"]
        )
        logger.debug(f"Saving result for device {self.name} with ip address {self.ip}.")
        logger.debug(result)
        result.save()
        id = 0
        for emeter in response["emeters"]:
            emeter_result = Shelly3EMEmeterResult(
                device=self,
                date=result.date,
                emeter_id=id,
                power=emeter["power"],
                pf=emeter["pf"],
                current=emeter["current"],
                voltage=emeter["voltage"],
                total=emeter["total"],
                total_returned=emeter["total_returned"],
            )
            emeter_result.save()
            logger.debug(f"Saving emeter result for with emeter_id {id}.")
            logger.debug(emeter_result)
            id += 1
        logger.debug(f"Results for device {self.name} with ip address {self.ip} saved.")
        logger.debug(result)
        return result

    class Meta:
        db_table = "shelly3em_devices"


class Shelly3EMResult(CPkModel):
    date = models.DateTimeField(auto_now_add=True, primary_key=True)
    device = models.ForeignKey(
        Shelly3EMDevice, on_delete=models.PROTECT, primary_key=True
    )

    total_power = models.FloatField()

    def __repr__(self):
        return "<Result(deivce_id='%s', total_power='%s', date='%s')>" % (
            self.device_id,
            self.total_power,
            self.date,
        )

    class Meta:
        managed = False  # for CompositePK *1
        db_table = "shelly3em_results"
        unique_together = (("device", "date"),)  # for CompositePK


class Shelly3EMEmeterResult(CPkModel):
    date = models.DateTimeField(primary_key=True)
    device = models.ForeignKey(
        Shelly3EMDevice, on_delete=models.PROTECT, primary_key=True
    )
    emeter_id = models.IntegerField(primary_key=True)

    emeters = CompositeForeignKey(
        Shelly3EMResult,
        on_delete=models.PROTECT,
        related_name="emeters",
        to_fields={"device": "device", "date": "date"},
    )

    power = models.FloatField()
    pf = models.FloatField()
    current = models.FloatField()
    voltage = models.FloatField()
    total = models.FloatField()
    total_returned = models.FloatField()

    def __repr__(self):
        return (
            "<EmeterResult(device_id='%s', result='%s', emeter_id='%s', power='%s', pf='%s', current='%s', voltage='%s', total='%s', total_returned='%s')>"
            % (
                self.device_id,
                self.result,
                self.emeter_id,
                self.power,
                self.pf,
                self.current,
                self.voltage,
                self.total,
                self.total_returned,
            )
        )

    class Meta:
        managed = False  # for CompositePK *1
        db_table = "shelly3em_emeter_results"
        unique_together = (("device", "date", "emeter_id"),)  # for CompositePK
