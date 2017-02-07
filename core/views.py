# coding: utf-8
import logging

from django.conf import settings
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from core import serializers
from sms_devino.client import DevinoClient, DevinoException
from sw_rest_auth.permissions import CodePermission
from . import models

logger = logging.getLogger('sms_service')


def index(request):
    return redirect('/doc/')


@api_view(['POST'])
@permission_classes((CodePermission.decorate(code='SMS_SEND'),))
def send(request):
    """
    Send sms resource
    ---
    serializer: serializers.Sms
    responseMessages:
        - code: 200
        - code: 400
        - code: 401
        - code: 403
    """
    sms_serializer = serializers.Sms(data=request.data)
    sms_serializer.is_valid(raise_exception=True)
    sms = sms_serializer.save()

    destination_address = sms_serializer.data['destination_address']
    logger.info('Create sms request', extra={'destination_address': destination_address})

    sms_client = DevinoClient(login=settings.DEVINO_LOGIN, password=settings.DEVINO_PASSWORD)
    try:
        result = sms_client.send_one(
            source_address=sms.source_address,
            destination_address=sms.destination_address,
            message=sms.message,
            validity_minutes=sms.validity_minutes,
        )
        logger.info('Send sms', extra={'destination_address': destination_address})

        models.SmsSendResult.objects.create(sms=sms, is_success=True)
        for sms_id in result.sms_ids:
            models.SmsPart.objects.create(sms=sms, external_id=sms_id)

    except DevinoException as ex:
        models.SmsSendResult.objects.create(sms=sms, is_success=False)
        error_serializer = serializers.SmsSendError.register_exception(sms, ex)
        error_data = error_serializer.data
        error_data['sms'] = sms_serializer.data
        logger.warning('Send sms error', extra={'destination_address': destination_address}, exc_info=True)
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

    return Response(sms_serializer.data)


@api_view(['GET'])
@permission_classes((CodePermission.decorate(code='SMS_GET_STATE'),))
def get_state(request):
    """
    Get sms status
    ---
    parameters:
        - name: sms
          type: string
          required: true
          description: uuid of sent sms
          paramType: query

    type:
        have_problems:
            required: true
            type: boolean
            description: Have any of the sms parts delivery problems

        all_delivered:
            required: true
            type: boolean
            description: Have all of the sms parts delivered successfully

        parts:
            required: true
            type: array
            description: Detailed info about each of sms part


    responseMessages:
        - code: 200
        - code: 400
        - code: 401
        - code: 403
    """
    serializer = serializers.GetState(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    sms = serializer.validated_data['sms']

    # TODO: доработать так, чтобы в devino за результатами ходили, только если у СМС не конечный статус, в противном случае брать данные из локальной базы
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
        logger.warning('Get sms error', extra={'sms_uuid': sms.uuid}, exc_info=True)
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

    qs = models.SmsPartSendState.objects.filter(sms_part__sms=sms)
    state_serializer = serializers.SmsPartSendState(qs, many=True)

    result = {
        'have_problems': any([1 <= s.code <= 100 for s in qs]),
        'all_delivered': all([s.code == 0 for s in qs]),
        'parts': state_serializer.data,
    }
    logger.debug('Requested sms state', extra=result)
    return Response(result)
