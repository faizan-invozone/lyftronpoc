from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from .serializers import DatabaseConnectionSerializer, IntegrationSerializer
from .models import DatabaseConnecion, Integration


class DatabaseConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = DatabaseConnectionSerializer
    queryset = DatabaseConnecion.objects.all()


class IntegrationViewSet(viewsets.ModelViewSet):
    serializer_class = IntegrationSerializer
    queryset = Integration.objects.all()


def test_mysql_connection(params):
    pass

class TestConnection(APIView):

    def post(self, request, format=None):
        request_data = request.data
        