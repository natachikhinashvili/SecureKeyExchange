"""
URL configuration for exchangekey project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from views.secretexchangeview import SecretExchangeView
from views.keygenerationview import KeyGenerationView
from channelviewset import ChannelViewSet
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("list_channels/", ChannelViewSet.as_view({'get': 'list'}), name='list_channels'),
    path('secret-exchange/', SecretExchangeView.as_view(), name='secret-exchange'),
    path('key-generation/', KeyGenerationView.as_view(), name='key-generation'),
]
