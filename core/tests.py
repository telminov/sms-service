# coding: utf-8
from decimal import Decimal
from django.test import mock
from django.utils.timezone import now
from rest_framework import test, status
from rest_framework.reverse import reverse
from sms_devino.client import SmsState
import sw_rest_auth.tests
from . import views
from . import models
from . import factories


class SendTestCase(sw_rest_auth.tests.AuthTestCaseMixin, test.APITestCase):
    url = reverse(views.send)
    perm = 'SMS_SEND'

    send_params = {
        'source_address': 'MyOrg',
        'destination_address': '+7 (903) 345-67-89',
        'message': 'Hello!',
        'validity_minutes': 3,
    }

    @mock.patch('core.views.DevinoClient')
    def test_send_success(self, DevinoClientMock):
        DevinoClientMock.return_value.send_one.return_value.sms_ids = [1, 2, 3]
        self.assertFalse(models.Sms.objects.exists())

        response = self.client.post(self.url, self.send_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertTrue(models.Sms.objects.exists())
        self.assertTrue(models.SmsSendResult.objects.get().is_success)
        self.assertEqual(
            models.SmsPart.objects.count(),
            len(DevinoClientMock.return_value.send_one.return_value.sms_ids),
        )

    @mock.patch('core.views.DevinoClient')
    def test_send_error(self, DevinoClientMock):
        DevinoClientMock.return_value.send_one.side_effect = views.DevinoException('all broke!')
        self.assertFalse(models.Sms.objects.exists())

        response = self.client.post(self.url, self.send_params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.data)
        self.assertTrue(models.Sms.objects.exists())
        self.assertFalse(models.SmsSendResult.objects.get().is_success)
        self.assertTrue(models.SmsSendError.objects.exists())


class GetStateTestCase(sw_rest_auth.tests.AuthTestCaseMixin, test.APITestCase):
    url = reverse(views.get_state)
    perm = 'SMS_GET_STATE'

    def generate_data(self):
        sms = factories.Sms()
        factories.SmsSendResult(sms=sms)
        factories.SmsPart(sms=sms)
        return sms

    def get_sms_state(self) -> SmsState:
        return SmsState(
            code=0,
            description='ok',
            price=Decimal(1.5),
            creation_dt=now(),
            submitted_dt=now(),
            result_dt=now(),
            reported_dt=now(),
        )

    def assertState(self, model_state: models.SmsPartSendState, sms_state: SmsState):
        self.assertEqual(model_state.code, sms_state.code)
        self.assertEqual(model_state.description, sms_state.description)
        self.assertEqual(model_state.price, sms_state.price)
        self.assertEqual(model_state.creation_dt, sms_state.creation_dt)
        self.assertEqual(model_state.submitted_dt, sms_state.submitted_dt)
        self.assertEqual(model_state.result_dt, sms_state.result_dt)
        self.assertEqual(model_state.reported_dt, sms_state.reported_dt)

    @mock.patch('core.views.DevinoClient')
    def test_get_status_success(self, DevinoClientMock):
        sms_state = self.get_sms_state()
        DevinoClientMock.return_value.get_state.return_value = sms_state

        sms = self.generate_data()
        self.assertFalse(models.SmsPartSendState.objects.exists())

        params = {'sms': sms.uuid}
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        state = models.SmsPartSendState.objects.get()
        self.assertState(state, sms_state)
        self.assertFalse(response.data['have_problems'])
        self.assertTrue(response.data['all_delivered'])

    @mock.patch('core.views.DevinoClient')
    def test_get_status_error(self, DevinoClientMock):
        DevinoClientMock.return_value.get_state.side_effect = views.DevinoException('all broke!')

        sms = self.generate_data()
        params = {'sms': sms.uuid}
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)