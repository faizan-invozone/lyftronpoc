from django.shortcuts import render
from rest_framework import viewsets
from .serializers import DatabaseConnectionSerializer, IntegrationSerializer
from .models import DatabaseConnecion, Integration


class DatabaseConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = DatabaseConnectionSerializer
    queryset = DatabaseConnecion.objects.all()


class IntegrationViewSet(viewsets.ModelViewSet):
    serializer_class = IntegrationSerializer
    queryset = Integration.objects.all()
