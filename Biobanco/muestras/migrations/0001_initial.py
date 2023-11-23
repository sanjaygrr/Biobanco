# Generated by Django 4.2.7 on 2023-11-23 03:05

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id_role', models.AutoField(primary_key=True, serialize=False)),
                ('role_name', models.CharField(max_length=15)),
            ],
            options={
                'db_table': 'ROLE',
            },
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id_sample', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('id_subject', models.CharField(max_length=10)),
                ('date_sample', models.DateField()),
                ('ml_volume', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('state_analysis', models.BooleanField(default=False, help_text='Valores: 0. No analizada 1. Enviada a análisis')),
                ('state_preservation', models.BooleanField(default=False, help_text='Valores: 0. Normal 1. Descongelada')),
                ('specification', models.CharField(max_length=10)),
                ('SHIPMENT_id_shipment', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'SAMPLE',
            },
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id_shipment', models.AutoField(primary_key=True, serialize=False)),
                ('date_shipment', models.DateField()),
                ('laboratory', models.CharField(max_length=30)),
                ('analysis', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'SHIPMENT',
            },
        ),
        migrations.CreateModel(
            name='StorageType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_storagetype', models.IntegerField(choices=[(1, 'Caja'), (2, 'Rack'), (3, 'Freezer')], unique=True)),
            ],
            options={
                'verbose_name': 'Tipo de Almacenamiento',
                'verbose_name_plural': 'Tipos de Almacenamiento',
                'db_table': 'STORAGE_TYPE',
            },
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('storage_name', models.CharField(max_length=9)),
                ('storage_state', models.BooleanField(default=True)),
                ('storage_description', models.CharField(max_length=50)),
                ('STORAGE_TYPE_id_storagetype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='muestras.storagetype')),
            ],
            options={
                'verbose_name': 'Almacenamiento',
                'verbose_name_plural': 'Almacenamientos',
                'db_table': 'STORAGE',
            },
        ),
        migrations.CreateModel(
            name='SampleEvent',
            fields=[
                ('id_event', models.AutoField(primary_key=True, serialize=False)),
                ('event_user', models.CharField(max_length=15)),
                ('event_date', models.DateField()),
                ('action', models.CharField(max_length=15)),
                ('action_information', models.CharField(max_length=100)),
                ('SAMPLE_id_sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='muestras.sample')),
            ],
            options={
                'db_table': 'SAMPLE_EVENT',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id_location', models.AutoField(primary_key=True, serialize=False)),
                ('cell', models.IntegerField(blank=True, null=True)),
                ('SAMPLE_id_sample_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='muestras.sample')),
                ('STORAGE_TYPE_id_storagetype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='muestras.storagetype')),
                ('STORAGE_id_storage_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='muestras.storage')),
            ],
            options={
                'db_table': 'LOCATION',
            },
        ),
    ]
