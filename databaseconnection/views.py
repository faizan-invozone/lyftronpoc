from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DatabaseConnectionSerializer, IntegrationSerializer
from .models import DatabaseConnecion, Integration
import subprocess
import requests
import json
from utils.mysql_meta import test_mysql_connection
from django_filters.rest_framework import DjangoFilterBackend
from utils.postgresql_target import test_postgresql_connection


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

def test_postgresql_credentials(params):
    host = params.get('host', None)
    port = params.get('port', None)
    user = params.get('user', None)
    password = params.get('password', None)
    test = test_postgresql_connection(host, port, user, password)
    return test

def test_api(params):
    endpoint = params.get('endpoint')
    if not endpoint:
        return False
    try:
        custom_endpoint = endpoint.split('//')
        custom_endpoint[0] = '{}//{}:{}@'.format(custom_endpoint[0], params.get('username', ''), params.get('password', ''))
        custom_endpoint = ''.join(custom_endpoint)
        res = requests.get(url=custom_endpoint)
        res_data = json.loads(res.text)
        if 'error' in res_data[0].keys():
            return False
        return True
    except Exception as e:
        return False



class TestConnection(APIView):

    def post(self, request, format=None):
        request_data = request.data
        test = None
        endpoint = request_data.get('endpoint', None)
        if endpoint:
            test = test_api(request_data)
        password = request_data.get('user', None)
        if password == 'asim':
            test = test_postgresql_credentials(request_data)
        elif not endpoint:
            test = test_mysql_credentials(request_data)
        if not test:
            return Response(data={'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'status': 'Success'}, status=status.HTTP_200_OK)