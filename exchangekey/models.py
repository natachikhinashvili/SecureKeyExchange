from django.contrib.auth.models import User
from django.db import models

class Channel(models.Model):
    class Meta:
        app_label = 'exchangekey'
    sender_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_channels')
    recipient_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_channels')
    name = models.CharField(max_length=255, unique=True)
    accepted = models.BooleanField(default=False)
    initial_sender_secret = models.TextField()
    initial_recipient_secret = models.TextField()

    def __str__(self):
        return self.name

class SecretExchange(models.Model):
    class Meta:
        app_label = 'exchangekey'
    channel = models.OneToOneField(Channel, on_delete=models.CASCADE)
    sender_secret = models.CharField(max_length=512)  # Storing large secrets
    recipient_secret = models.CharField(max_length=512, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SecretExchange for channel {self.channel.id}"
