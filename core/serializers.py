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
        extra_kwargs = {'destination_address': {'max_length': 20}}

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
    def register_exception(cls, sms: models.Sms, ex: DevinoException) -> 'SmsSendError':
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


class GetState(serializers.Serializer):
    sms = serializers.UUIDField()

    def validate_sms(self, value):
        try:
            sms = models.Sms.objects.get(uuid=value)

            if not sms.send_result.is_success:
                raise serializers.ValidationError('Sms was not successful sent')

            if not sms.parts.exists():
                raise serializers.ValidationError('No info about sent sms')

            return sms
        except models.Sms.DoesNotExist:
            raise serializers.ValidationError('Sms with uuid "{0}" not found'.format(value))


class SmsPartSendState(serializers.ModelSerializer):
    sms_part_external_id = serializers.SerializerMethodField()

    class Meta:
        model = models.SmsPartSendState
        exclude = ('id', 'sms_part', )

    def get_sms_part_external_id(self, obj):
        return obj.sms_part.external_id
