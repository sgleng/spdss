# Generated by Django 3.0.4 on 2020-04-23 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0013_auto_20200423_0830'),
    ]

    operations = [
        migrations.RenameField(
            model_name='skills',
            old_name='grossprofit',
            new_name='gross_profit',
        ),
    ]
