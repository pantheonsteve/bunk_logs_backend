# Generated by Django 5.0.13 on 2025-03-12 03:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cabin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('capacity', models.PositiveIntegerField()),
                ('location', models.CharField(blank=True, max_length=255)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'cabin',
                'verbose_name_plural': 'cabins',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'session',
                'verbose_name_plural': 'sessions',
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('unit_head', models.ForeignKey(limit_choices_to={'role': 'UNIT_HEAD'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_units', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'unit',
                'verbose_name_plural': 'units',
            },
        ),
        migrations.CreateModel(
            name='Bunk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('counselors', models.ManyToManyField(limit_choices_to={'role': 'COUNSELOR'}, related_name='assigned_bunks', to=settings.AUTH_USER_MODEL)),
                ('cabin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bunks', to='bunks.cabin')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bunks', to='bunks.session')),
                ('unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bunks', to='bunks.unit')),
            ],
            options={
                'verbose_name': 'bunk',
                'verbose_name_plural': 'bunks',
                'unique_together': {('cabin', 'session')},
            },
        ),
    ]
