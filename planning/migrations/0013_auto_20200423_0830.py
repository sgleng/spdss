# Generated by Django 3.0.4 on 2020-04-23 08:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0012_auto_20200420_1441'),
    ]

    operations = [
        migrations.RenameField(
            model_name='skills',
            old_name='revenue',
            new_name='grossprofit',
        ),
    ]
