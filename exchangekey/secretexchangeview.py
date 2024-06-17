import os
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from models import Channel, SecretExchange
from serializers import SecretExchangeSerializer

class SecretExchangeView(APIView):
    def post(self, request, *args, **kwargs):
        channel_id = request.data.get('channel_id')
        try:
            channel = Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            return Response({'detail': 'Channel not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != channel.sender_user and request.user != channel.recipient_user:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        if not hasattr(channel, 'secretexchange'):
            secret_key = int.from_bytes(os.urandom(32), byteorder='big')

            initial_sender_secret = pow(settings.BASE, secret_key, settings.MODULUS)
            initial_recipient_secret = None

            if request.user == channel.sender_user:
                initial_sender_secret = pow(settings.BASE, secret_key, settings.MODULUS)
                SecretExchange.objects.create(
                    channel=channel,
                    sender_secret=initial_sender_secret,
                )
                return Response({
                    'secret_key': secret_key,
                    'sender_secret': initial_sender_secret,
                }, status=status.HTTP_201_CREATED)

            if request.user == channel.recipient_user:
                initial_recipient_secret = pow(settings.BASE, secret_key, settings.MODULUS)
                secret_exchange = SecretExchange.objects.get(channel=channel)
                secret_exchange.recipient_secret = initial_recipient_secret
                secret_exchange.save()
                return Response({
                    'secret_key': secret_key,
                    'recipient_secret': initial_recipient_secret,
                }, status=status.HTTP_201_CREATED)

        return Response({'detail': 'Secret exchange already exists.'}, status=status.HTTP_400_BAD_REQUEST)
