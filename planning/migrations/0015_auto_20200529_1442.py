# Generated by Django 3.0.6 on 2020-05-29 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0014_auto_20200423_0832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shifts',
            name='length',
            field=models.FloatField(default=0),
        ),
    ]
