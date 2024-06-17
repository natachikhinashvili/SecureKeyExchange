import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exchangekey.settings')

django.setup()
from django.test import TestCase
from django.contrib.auth.models import User
from models.channel import Channel
from django.urls import reverse
from models.secretexchange import SecretExchange
from rest_framework.test import APIClient
from rest_framework import status

class KeyGenerationTestCase(TestCase):
    def setUp(self):
        self.sender_user = User.objects.create_user(username='sender', password='senderpassword')
        self.recipient_user = User.objects.create_user(username='recipient', password='recipientpassword')
        self.secret_key=int.from_bytes(os.urandom(32), byteorder='big')
        self.recipient_key=int.from_bytes(os.urandom(32), byteorder='big')

        self.channel = Channel.objects.create(
            sender_user=self.sender_user,
            recipient_user=self.recipient_user,
            name='Test Channel',
            initial_sender_secret='Sender secret',
            initial_recipient_secret='Recipient secret'
        )

        self.secret_exchange = SecretExchange.objects.create(
            channel=self.channel,
            sender_secret=self.secret_key,  
            recipient_secret=self.recipient_key 
        )

        self.client = APIClient()

    def test_key_generation_sender(self):
        """Test KeyGenerationView for sender user"""
        self.client.force_authenticate(user=self.sender_user)

        url = reverse('key-generation')
        data = {
            'channel_id': self.channel.id,
            'secret_key': self.secret_key
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.data)

    def test_key_generation_recipient(self):
        """Test KeyGenerationView for recipient user"""
        self.client.force_authenticate(user=self.recipient_user)

        url = reverse('key-generation')
        data = {
            'channel_id': self.channel.id,
            'secret_key': self.secret_key
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.data)

    def test_key_generation_unauthorized(self):
        """Test KeyGenerationView unauthorized access"""
        unauthorized_user = User.objects.create_user(username='unauthorized', password='unauthorizedpassword')
        self.client.force_authenticate(user=unauthorized_user)

        url = reverse('key-generation')
        data = {
            'channel_id': self.channel.id,
            'secret_key': self.secret_key
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_key_generation_invalid_secret_key(self):
        """Test KeyGenerationView with invalid secret key"""
        self.client.force_authenticate(user=self.sender_user)

        url = reverse('key-generation')
        data = {
            'channel_id': self.channel.id,
            'secret_key': 'invalid_secret_key'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid secret key.', response.data['detail'])

    def test_key_generation_missing_params(self):
        """Test KeyGenerationView with missing parameters"""
        self.client.force_authenticate(user=self.sender_user)

        url = reverse('key-generation')
        data = {}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Channel ID and secret key are required.', response.data['detail'])

    def test_key_generation_secret_not_generated(self):
        """Test KeyGenerationView when secret for the other party is not yet generated"""
        self.client.force_authenticate(user=self.sender_user)

        self.secret_exchange.recipient_secret = None
        self.secret_exchange.save()

        url = reverse('key-generation')
        data = {
            'channel_id': self.channel.id,
            'secret_key': self.secret_key
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Recipient secret not yet generated.', response.data['detail'])

