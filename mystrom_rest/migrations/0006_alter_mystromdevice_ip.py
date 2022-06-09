# Generated by Django 4.0.5 on 2022-06-08 22:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mystrom_rest', '0005_alter_mystromdevice_ip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mystromdevice',
            name='ip',
            field=models.CharField(max_length=16, validators=[django.core.validators.RegexValidator(message='Not valid IP Address', regex='^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')]),
        ),
    ]