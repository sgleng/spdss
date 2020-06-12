# Generated by Django 3.0.4 on 2020-04-18 12:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0006_skills_workplaces'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerskills',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='skills',
            name='workplaces',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterUniqueTogether(
            name='workerskills',
            unique_together={('date', 'worker', 'skill')},
        ),
    ]