# Generated by Django 3.0.4 on 2020-04-18 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0009_auto_20200418_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='skills',
            name='revenue',
            field=models.FloatField(default=0),
        ),
    ]
