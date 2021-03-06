# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-19 12:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sms',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('source_address', models.CharField(max_length=15)),
                ('destination_address', models.CharField(max_length=11)),
                ('message', models.TextField(max_length=2000)),
                ('validity_minutes', models.SmallIntegerField(default=0)),
                ('dc', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SmsPart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(max_length=255, unique=True)),
                ('sms', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parts', to='core.Sms')),
            ],
        ),
        migrations.CreateModel(
            name='SmsPartSendState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField()),
                ('description', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('creation_dt', models.DateTimeField(null=True)),
                ('submitted_dt', models.DateTimeField(null=True)),
                ('result_dt', models.DateTimeField()),
                ('reported_dt', models.DateTimeField(null=True)),
                ('sms_part', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.SmsPart')),
            ],
        ),
        migrations.CreateModel(
            name='SmsSendError',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('code', models.IntegerField(null=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('dt', models.DateTimeField(auto_now_add=True)),
                ('sms', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='send_error', to='core.Sms')),
            ],
        ),
        migrations.CreateModel(
            name='SmsSendResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_dt', models.DateTimeField(auto_now_add=True)),
                ('is_success', models.BooleanField()),
                ('sms', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='send_result', to='core.Sms')),
            ],
        ),
    ]
