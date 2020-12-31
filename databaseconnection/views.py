from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DatabaseConnectionSerializer, IntegrationSerializer
from .models import DatabaseConnecion, Integration


class DatabaseConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = DatabaseConnectionSerializer
    queryset = DatabaseConnecion.objects.all()


class IntegrationViewSet(viewsets.ModelViewSet):
    serializer_class = IntegrationSerializer
    queryset = Integration.objects.all()


def test_mysql_connection(params):
    host = params.get('host', None)
    port = params.get('port', None)
    user = params.get('user', None)
    password = params.get('password', None)
    # Farhan your code will be here.
    # Please return true if connection succeeded else false 
    return True

class TestConnection(APIView):

    def post(self, request, format=None):
        request_data = request.data
        test = test_mysql_connection(request_data)
        if not test:
            return Response(data={'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'status': 'Success'}, status=status.HTTP_200_OK)