from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DatabaseConnectionSerializer, IntegrationSerializer
from .models import DatabaseConnecion, Integration
import subprocess
from utils.mysql_meta import test_mysql_connection
from django_filters.rest_framework import DjangoFilterBackend


class DatabaseConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = DatabaseConnectionSerializer
    queryset = DatabaseConnecion.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['connection_type']


class IntegrationViewSet(viewsets.ModelViewSet):
    serializer_class = IntegrationSerializer
    queryset = Integration.objects.all()


def test_mysql_credentials(params):
    host = params.get('host', None)
    port = params.get('port', None)
    user = params.get('user', None)
    password = params.get('password', None)
    test = test_mysql_connection(host, port, user, password)
    return test

class TestConnection(APIView):

    def post(self, request, format=None):
        request_data = request.data
        test = test_mysql_credentials(request_data)
        if not test:
            return Response(data={'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'status': 'Success'}, status=status.HTTP_200_OK)