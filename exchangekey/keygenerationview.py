from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from models import Channel, SecretExchange

class KeyGenerationView(APIView):
    def post(self, request, *args, **kwargs):
        channel_id = request.data.get('channel_id')
        secret_key = request.data.get('secret_key')
        
        if not channel_id or not secret_key:
            return Response({'detail': 'Channel ID and secret key are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            channel = Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            return Response({'detail': 'Channel not found.'}, status=status.HTTP_404_NOT_FOUND)

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
            if not secret_exchange.initial_recipient_secret:
                return Response({'detail': 'Recipient secret not yet generated.'}, status=status.HTTP_400_BAD_REQUEST)
            shared_key = pow(int(secret_exchange.initial_recipient_secret), secret_key, settings.MODULUS)
            return Response({'key': shared_key}, status=status.HTTP_200_OK)

        if request.user == channel.recipient_user:
            if not secret_exchange.initial_sender_secret:
                return Response({'detail': 'Sender secret not yet generated.'}, status=status.HTTP_400_BAD_REQUEST)
            shared_key = pow(int(secret_exchange.initial_sender_secret), secret_key, settings.MODULUS)
            return Response({'key': shared_key}, status=status.HTTP_200_OK)

        return Response({'detail': 'Unexpected error.'}, status=status.HTTP_400_BAD_REQUEST)
