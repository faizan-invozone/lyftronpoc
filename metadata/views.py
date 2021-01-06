from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from databaseconnection.models import Integration
import json
from utils.mysql_meta import mysql_meta_
from utils.postgresql_target import replicate_to_target


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


def replicate_db_structure(integration, structure):
    '''
        This function is being used for getting connection parameters and replication of db structure
        params:
            integration
    '''
    try:
        target = json.loads(integration.destination)
        host = target['host']
        port = target['port']
        user = target['user']
        password = target['password']
        replicate_to_target(host, port, user, password, structure)
        return True
    except Exception as e:
        return False

class ReplicateMetaData(APIView):

    def post(self, request, format=None):
        structure = request.data.get('structure')
        integration_id = request.data.get('integration')
        if not integration_id:
            return Response(data={'error': 'Please provide integration'}, status=status.HTTP_400_BAD_REQUEST)
        integration = None
        try:
            integration = Integration.objects.get(pk=integration_id)
        except Exception as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if not structure:
            return Response(data={'error': 'Please provide Metadata structure.'}, status=status.HTTP_400_BAD_REQUEST)
        replication = replicate_db_structure(integration, structure)
        if not replication:
            return Response(data={'error': 'Something went wrong while replicating DB structure.'}, 
            status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'success': 'Successfully received structure with integration ' + integration.name})
