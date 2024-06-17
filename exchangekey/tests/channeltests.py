import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exchangekey.settings')

django.setup()
from django.test import TestCase
from django.contrib.auth.models import User
from models import Channel

class ChannelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')

    def test_channel_creation(self):
        """Test creation of Channel objects"""
        channel = Channel.objects.create(
            sender_user=self.user1,
            recipient_user=self.user2,
            name='Test Channel',
            initial_sender_secret='Initial sender secret',
            initial_recipient_secret='Initial recipient secret'
        )

        self.assertEqual(Channel.objects.count(), 1)
        self.assertEqual(channel.sender_user, self.user1)
        self.assertEqual(channel.recipient_user, self.user2)
        self.assertEqual(channel.name, 'Test Channel')
        self.assertFalse(channel.accepted)
