# coding: utf-8
from django.utils.timezone import now
import factory
import factory.fuzzy
from . import models


class Sms(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Sms

    uuid = factory.Faker('uuid4')
    source_address = factory.fuzzy.FuzzyText(length=15)
    destination_address = factory.fuzzy.FuzzyText(length=11)
    message = factory.fuzzy.FuzzyText(length=70)
    dc = now().replace(microsecond=0)


class SmsSendResult(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SmsSendResult

    sms = factory.SubFactory(Sms)
    is_success = True
    send_dt = now().replace(microsecond=0)


class SmsPart(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SmsPart

    sms = factory.SubFactory(Sms)
    external_id = factory.Faker('uuid4')
