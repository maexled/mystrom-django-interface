# Generated by Django 5.0.7 on 2024-07-20 16:14

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("shelly3em_rest", "0003_auto_20240720_1610"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="shelly3ememeterresult",
            options={"managed": False},
        ),
        migrations.AlterModelOptions(
            name="shelly3emresult",
            options={"managed": False},
        ),
    ]