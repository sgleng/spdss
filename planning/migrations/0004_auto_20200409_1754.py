# Generated by Django 3.0.4 on 2020-04-09 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0003_availability_shifts_workers_workerskills'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workerskills',
            name='productivity',
            field=models.FloatField(default=0),
        ),
    ]