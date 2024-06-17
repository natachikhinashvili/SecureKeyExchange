from django.db import models
from .channel import Channel

class SecretExchange(models.Model):
    class Meta:
        app_label = 'exchangekey'
    channel = models.OneToOneField(Channel, on_delete=models.CASCADE)
    sender_secret = models.CharField(max_length=512)
    recipient_secret = models.CharField(max_length=512, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SecretExchange for channel {self.channel.id}"