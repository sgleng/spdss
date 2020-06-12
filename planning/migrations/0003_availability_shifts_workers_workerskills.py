# Generated by Django 3.0.4 on 2020-04-09 17:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0002_auto_20200409_1111'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shifts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('length', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Shifts',
            },
        ),
        migrations.CreateModel(
            name='Workers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Workers',
            },
        ),
        migrations.CreateModel(
            name='WorkerSkills',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productivity', models.IntegerField(default=0)),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.Skills')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.Workers')),
            ],
            options={
                'verbose_name_plural': 'Worker skills',
            },
        ),
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='planning.Shifts')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='planning.Workers')),
            ],
            options={
                'verbose_name_plural': 'Availability',
            },
        ),
    ]