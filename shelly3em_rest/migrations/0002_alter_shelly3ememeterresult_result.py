# Generated by Django 4.0.5 on 2022-09-14 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("shelly3em_rest", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shelly3ememeterresult",
            name="result",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="emeters",
                to="shelly3em_rest.shelly3emresult",
            ),
        ),
    ]
