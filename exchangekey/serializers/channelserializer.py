from rest_framework import serializers
from models.channel import Channel

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'sender_user', 'recipient_user', 'name', 'initial_sender_secret', 'initial_recipient_secret', 'accepted']
