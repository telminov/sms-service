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


@api_view(['GET'])
@permission_classes((CodePermission.decorate(code='SMS_GET_STATE'),))
def get_state(request):
    serializer = serializers.GetState(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    sms = serializer.validated_data['sms']

    sms_client = DevinoClient(login=settings.DEVINO_LOGIN, password=settings.DEVINO_PASSWORD)
    try:
        for part in sms.parts.all():
            state = sms_client.get_state(part.external_id)
            data = {
                'code': state.code,
                'description': state.description,
                'price': state.price,
                'creation_dt': state.creation_dt,
                'submitted_dt': state.submitted_dt,
                'result_dt': state.result_dt,
                'reported_dt': state.reported_dt,
            }

            sms_part_state, created = models.SmsPartSendState.objects.get_or_create(sms_part=part, defaults=data)
            if not created:
                models.SmsPartSendState.objects.filter(sms_part=part).update(**data)

    except DevinoException as ex:
        error_data = {'message': ex.message}
        if ex.error and ex.error.code:
            error_data['code'] = ex.error.code
        if ex.error and ex.error.description:
            error_data['description'] = ex.error.description
        return Response(error_data, status=400)

    qs = models.SmsPartSendState.objects.filter(sms_part__sms=sms)
    state_serializer = serializers.SmsPartSendState(qs, many=True)
    return Response(state_serializer.data)
