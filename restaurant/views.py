from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from restaurant.models import *
from restaurant.serializers import *
from restaurant.permissions import IsManager

# Create your views here.


class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    authentication_classes = (TokenAuthentication, )

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = [AllowAny]
            return [AllowAny(), ]
        else:
            self.permission_classes = [IsManager,]
            return [IsManager(), ]



