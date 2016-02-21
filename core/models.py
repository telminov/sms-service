# coding: utf-8
import uuid
from django.db import models


class Sms(models.Model):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    source_address = models.CharField(max_length=15)
    destination_address = models.CharField(max_length=11)
    message = models.TextField(max_length=2000)
    validity_minutes = models.SmallIntegerField(default=0)
    dc = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.uuid)


class SmsSendResult(models.Model):
    sms = models.OneToOneField(Sms, related_name='send_result')
    send_dt = models.DateTimeField(auto_now_add=True)
    is_success = models.BooleanField()


class SmsPart(models.Model):
    sms = models.ForeignKey(Sms, related_name='parts')
    external_id = models.CharField(max_length=255, unique=True)


class SmsSendError(models.Model):
    sms = models.OneToOneField(Sms, related_name='send_error')
    message = models.CharField(max_length=255)
    code = models.IntegerField(null=True)
    description = models.CharField(max_length=255, blank=True)
    dt = models.DateTimeField(auto_now_add=True)


class SmsPartSendState(models.Model):
    sms_part = models.OneToOneField(SmsPart)
    code = models.IntegerField()
    description = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=5, null=True)
    creation_dt = models.DateTimeField(null=True)
    submitted_dt = models.DateTimeField(null=True)
    result_dt = models.DateTimeField()
    reported_dt = models.DateTimeField(null=True)
