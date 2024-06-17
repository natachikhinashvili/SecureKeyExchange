import os
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from models.channel import Channel
from models.secretexchange import SecretExchange

class SecretExchangeView(APIView):
    def post(self, request, *args, **kwargs):
        channel_id = request.data.get('channel_id')
        
        if not channel_id:
            return Response({'detail': 'Channel ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        channel = get_object_or_404(Channel, id=channel_id)
        if request.user != channel.sender_user and request.user != channel.recipient_user:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            secret_exchange = SecretExchange.objects.get(channel=channel)
        except SecretExchange.DoesNotExist:
            secret_key = int.from_bytes(os.urandom(32), byteorder='big')

            if request.user == channel.sender_user:
                initial_sender_secret = pow(secret_key, settings.BASE, int(settings.MODULUS, 16))
                SecretExchange.objects.create(
                    channel=channel,
                    sender_secret=str(initial_sender_secret),
                )
                return Response({
                    'secret_key': secret_key,
                    'sender_secret': initial_sender_secret,
                }, status=status.HTTP_201_CREATED)

            elif request.user == channel.recipient_user:
                initial_recipient_secret = pow(secret_key, settings.BASE, int(settings.MODULUS, 16))
                SecretExchange.objects.create(
                    channel=channel,
                    recipient_secret=str(initial_recipient_secret),
                )
                return Response({
                    'secret_key': secret_key,
                    'recipient_secret': initial_recipient_secret,
                }, status=status.HTTP_201_CREATED)

        if request.user == channel.sender_user:
            return Response({
                'secret_key': secret_exchange.sender_secret,
                'sender_secret': secret_exchange.sender_secret,
            }, status=status.HTTP_200_OK)

        elif request.user == channel.recipient_user:
            return Response({
                'secret_key': secret_exchange.recipient_secret,
                'recipient_secret': secret_exchange.recipient_secret,
            }, status=status.HTTP_200_OK)

        return Response({'detail': 'Unexpected error.'}, status=status.HTTP_400_BAD_REQUEST)
