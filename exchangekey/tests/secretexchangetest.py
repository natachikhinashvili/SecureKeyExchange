import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exchangekey.settings')

django.setup()
from django.test import TestCase
from django.contrib.auth.models import User
from models import Channel
from django.urls import reverse
from models import Channel, SecretExchange
from rest_framework.test import APIClient
from rest_framework import status

class SecretExchangeTestCase(TestCase):
    def setUp(self):
        self.sender_user = User.objects.create_user(username='sender', password='senderpassword')
        self.recipient_user = User.objects.create_user(username='recipient', password='recipientpassword')

        self.channel = Channel.objects.create(
            sender_user=self.sender_user,
            recipient_user=self.recipient_user,
            name='Test Channel',
            initial_sender_secret='Initial sender secret',
            initial_recipient_secret='Initial recipient secret'
        )

        self.secret_exchange = SecretExchange.objects.create(
            channel=self.channel,
            sender_secret='Sender secret',
            recipient_secret='Recipient secret'
        )

        self.client = APIClient()

    def test_secret_exchange_view_sender(self):
        """Test SecretExchangeView for sender user"""
        self.client.force_authenticate(user=self.sender_user)

        url = reverse('secret-exchange')
        data = {'channel_id': self.channel.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('secret_key', response.data)
        self.assertIn('sender_secret', response.data)

    def test_secret_exchange_view_recipient(self):
        """Test SecretExchangeView for recipient user"""
        self.client.force_authenticate(user=self.recipient_user)

        url = reverse('secret-exchange')
        data = {'channel_id': self.channel.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('secret_key', response.data)
        self.assertIn('recipient_secret', response.data)

    def test_secret_exchange_view_unauthorized(self):
        """Test SecretExchangeView unauthorized access"""
        unauthorized_user = User.objects.create_user(username='unauthorized', password='unauthorizedpassword')
        self.client.force_authenticate(user=unauthorized_user)

        url = reverse('secret-exchange')
        data = {'channel_id': self.channel.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_secret_exchange_view_missing_channel_id(self):
        """Test SecretExchangeView with missing channel_id"""
        self.client.force_authenticate(user=self.sender_user)

        url = reverse('secret-exchange')
        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Channel ID is required.', response.data['detail'])

