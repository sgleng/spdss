# Generated by Django 3.0.4 on 2020-04-20 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0010_skills_revenue'),
    ]

    operations = [
        migrations.AddField(
            model_name='workers',
            name='preference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planning.WorkerSkills'),
        ),
    ]
