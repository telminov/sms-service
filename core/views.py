# coding: utf-8
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from core import serializers
from sms_devino.client import DevinoClient, DevinoException
from sw_rest_auth.permissions import CodePermission
from . import models


@api_view(['POST'])
@permission_classes((CodePermission.decorate(code='SMS_SEND'),))
def send(request):
    sms_serializer = serializers.Sms(data=request.data)
    sms_serializer.is_valid(raise_exception=True)
    sms = sms_serializer.save()

    sms_client = DevinoClient(login=settings.DEVINO_LOGIN, password=settings.DEVINO_PASSWORD)
    try:
        result = sms_client.send_one(
            source_address=sms.source_address,
            destination_address=sms.destination_address,
            message=sms.message,
            validity_minutes=sms.validity_minutes,
        )
        models.SmsSendResult.objects.create(sms=sms, is_success=True)
        for sms_id in result.sms_ids:
            models.SmsPart.objects.create(sms=sms, external_id=sms_id)

    except DevinoException as ex:
        models.SmsSendResult.objects.create(sms=sms, is_success=False)
        error_serializer = serializers.SmsSendError.process_exception(sms, ex)
        error_data = error_serializer.data
        error_data['sms'] = sms_serializer.data
        return Response(error_data, status=400)

    return Response(sms_serializer.data)


