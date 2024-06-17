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