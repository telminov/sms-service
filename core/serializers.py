# coding: utf-8
from rest_framework import serializers
from swutils.phone import gen_canonical_phone, CanonicalPhoneGenerationException
from sms_devino.client import DevinoException
from core import models


class Sms(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()

    class Meta:
        model = models.Sms
        fields = ('uuid', 'source_address', 'destination_address', 'message', 'validity_minutes', 'result')

    def get_result(self, obj):
        try:
            result = models.SmsSendResult.objects.get(sms=obj)
            return SmsSendResult(instance=result).data
        except models.SmsSendResult.DoesNotExist:
            return None

    def validate_destination_address(self, value):
        try:
            return gen_canonical_phone(value)
        except CanonicalPhoneGenerationException as ex:
            raise serializers.ValidationError(str(ex))


class SmsSendResult(serializers.ModelSerializer):
    class Meta:
        model = models.SmsSendResult
        fields = ('send_dt', 'is_success')


class SmsSendError(serializers.ModelSerializer):

    class Meta:
        model = models.SmsSendError
        fields = ('sms', 'message', 'code', 'description')

    @classmethod
    def process_exception(cls, sms: models.Sms, ex: DevinoException) -> 'SmsSendError':
        data = {
            'sms': sms.pk,
            'message': ex.message,
        }
        if ex.error:
            if ex.error.code:
                data['code'] = ex.error.code
            if ex.error.description:
                data['description'] = ex.error.description

        serializer = cls(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer
