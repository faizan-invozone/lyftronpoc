from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from databaseconnection.models import Integration
import json
from utils.mysql_meta import mysql_meta_


def get_mysql_credentials(sql_dialect, source):
    if sql_dialect.name.lower() == 'mysql':
        str_creds = source.credential
        creds = json.loads(str_creds)
        host = creds['host']
        port = creds['port']
        user = creds['user']
        password = creds['password']
        return host, port, user, password

def get_mysql_metadata(integration):
    host, port, user, password = get_mysql_credentials(integration.source.sql_dialect, integration.source)
    metadata = mysql_meta_(host,port,user,password)  
    return metadata

class ListMetaData(APIView):
    
    def post(self, request, format=None):
        integration_id = request.data.get('integration', None)
        if not integration_id:
            return Response(data={'error': 'Please provide integration ID'})
        integration = Integration.objects.filter(pk=integration_id)
        if not integration:
            return Response(data={'error': 'Integration not found'})
        integration = integration[0]
        metadata = get_mysql_metadata(integration)
        if not metadata:
            return Response(data={'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=metadata)



class ReplicateMetaData(APIView):

    def post(self, request, format=None):
        structure = request.data.get('structure')
        if not structure:
            return Response(data={'error': 'Please provide Metadata structure.'}, status=status.HTTP_417_EXPECTATION_FAILED)
        return Response(data={'success': 'Successfully received structure'})
