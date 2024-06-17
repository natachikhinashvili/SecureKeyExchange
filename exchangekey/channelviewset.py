from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from models.channel import Channel
from serializers.channelserializer import ChannelSerializer
import random
import string

class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender_user=self.request.user, name=self.generate_random_name())

    def generate_random_name(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    def get_queryset(self):
        user = self.request.user
        return Channel.objects.filter(sender_user=user)

    @action(detail=False, methods=['get'])
    def list_channels(self, request):
        user = request.user
        channels = Channel.objects.filter(sender_user=user)
        serializer = self.get_serializer(channels, many=True)
        return Response(serializer.data)