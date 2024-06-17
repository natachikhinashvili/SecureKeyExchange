from rest_framework import serializers
from models import SecretExchange

class SecretExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecretExchange
        fields = ['channel', 'sender_secret', 'recipient_secret']
