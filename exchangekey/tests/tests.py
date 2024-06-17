import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exchangekey.settings')

django.setup()

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from models import Channel, SecretExchange
import os
from django.conf import settings

class ChannelAPITestCase(APITestCase):
    def setUp(self):
        self.sender_user = User.objects.create_user(username='sender', password='password')
        self.recipient_user = User.objects.create_user(username='recipient', password='password')
        
        self.channel_data = {
            'recipient_user': self.recipient_user.id,
            'name': 'Test Channel'
        }

    def test_channel_creation_and_acceptance(self):
        self.client.login(username='sender', password='password')

        response = self.client.post('/channels/', self.channel_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        channel_id = response.data['id']

        response = self.client.post(f'/channels/{channel_id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()
        self.client.login(username='recipient', password='password')
        response = self.client.post(f'/channels/{channel_id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_secret_exchange_and_key_generation(self):
        self.client.login(username='sender', password='password')

        response = self.client.post('/channels/', self.channel_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        channel_id = response.data['id']

        response = self.client.post('/secret-exchange/', {'channel_id': channel_id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sender_secret_key = response.data['secret_key']
        initial_sender_secret = response.data['sender_secret']

        self.client.logout()
        self.client.login(username='recipient', password='password')
        response = self.client.post('/secret-exchange/', {'channel_id': channel_id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipient_secret_key = response.data['secret_key']
        initial_recipient_secret = response.data['recipient_secret']

        secret_exchange = SecretExchange.objects.get(channel_id=channel_id)
        self.assertEqual(secret_exchange.initial_sender_secret, str(initial_sender_secret))
        self.assertEqual(secret_exchange.initial_recipient_secret, str(initial_recipient_secret))

        self.client.logout()
        self.client.login(username='sender', password='password')
        response = self.client.post('/key-generation/', {'channel_id': channel_id, 'secret_key': sender_secret_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_sender_key = pow(int(initial_recipient_secret), sender_secret_key, settings.MODULUS)
        self.assertEqual(response.data['key'], expected_sender_key)

        self.client.logout()
        self.client.login(username='recipient', password='password')
        response = self.client.post('/key-generation/', {'channel_id': channel_id, 'secret_key': recipient_secret_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_recipient_key = pow(int(initial_sender_secret), recipient_secret_key, settings.MODULUS)
        self.assertEqual(response.data['key'], expected_recipient_key)