import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exchangekey.settings')
django.setup()

from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from models.channel import Channel
from rest_framework import status
from django.urls import reverse

class ChannelTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.channel = Channel.objects.create(
            sender_user=self.user1,
            recipient_user=self.user2,
            name='Test Channel',
            initial_sender_secret='Initial sender secret',
            initial_recipient_secret='Initial recipient secret'
        )

    def test_channel_creation(self):
        """Test creation of Channel objects"""
        self.assertEqual(Channel.objects.count(), 1)
        self.assertEqual(self.channel.sender_user, self.user1)
        self.assertEqual(self.channel.recipient_user, self.user2)
        self.assertEqual(self.channel.name, 'Test Channel')
        self.assertFalse(self.channel.accepted)

    def test_list_channels(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('list_channels'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)