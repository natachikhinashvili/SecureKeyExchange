from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from models.channel import Channel
from models.secretexchange import SecretExchange

class KeyGenerationView(APIView):
    def post(self, request, *args, **kwargs):
        channel_id = request.data.get('channel_id')
        secret_key = request.data.get('secret_key')
        
        if not channel_id or not secret_key:
            return Response({'detail': 'Channel ID and secret key are required.'}, status=status.HTTP_400_BAD_REQUEST)

        channel = get_object_or_404(Channel, id=channel_id)
        
        if request.user != channel.sender_user and request.user != channel.recipient_user:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            secret_exchange = SecretExchange.objects.get(channel=channel)
        except SecretExchange.DoesNotExist:
            return Response({'detail': 'Secret exchange not found for this channel.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            secret_key = int(secret_key)
        except ValueError:
            return Response({'detail': 'Invalid secret key.'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user == channel.sender_user:
            if not secret_exchange.recipient_secret:
                return Response({'detail': 'Recipient secret not yet generated.'}, status=status.HTTP_400_BAD_REQUEST)
            recipient_secret = int(secret_exchange.recipient_secret)
            shared_key = pow(recipient_secret, secret_key, int(settings.MODULUS,16))
            return Response({'key': shared_key}, status=status.HTTP_200_OK)

        elif request.user == channel.recipient_user:
            if not secret_exchange.sender_secret:
                return Response({'detail': 'Sender secret not yet generated.'}, status=status.HTTP_400_BAD_REQUEST)
            sender_secret = int(secret_exchange.sender_secret)
            shared_key = pow(sender_secret, secret_key, int(settings.MODULUS,16))
            return Response({'key': shared_key}, status=status.HTTP_200_OK)

        return Response({'detail': 'Unexpected error.'}, status=status.HTTP_400_BAD_REQUEST)
