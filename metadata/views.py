from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from databaseconnection.models import Integration
import json
import os
import requests
from utils.mysql_meta import mysql_meta_
from utils.postgresql_target import replicate_to_target
from utils.fetch_data import fetch_data_from_mysql
from utils.insert_into_target import insert_data_into_postgres_target
from utils.get_api_metadata import load_data_into_target_db
from utils.postgresql_target import test_postgresql_connection
from utils.tranf_elt import _do_transformation


def get_mysql_credentials(sql_dialect, source):
    if sql_dialect.name.lower() == 'mysql':
        str_creds = source.credential
        creds = json.loads(str_creds)
        host = creds['host']
        port = creds['port']
        user = creds['user']
        password = creds['password']
        return host, port, user, password

def get_postgresql_credentials(sql_dialect, source):
    if sql_dialect.name.lower() == 'postgresql':
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
        target = json.loads(integration.destination.credential)
        host = target['host']
        port = target['port']
        user = target['user']
        password = target['password']
        replicate_to_target(host, port, user, password, structure)
        return True
    except Exception as e:
        return False
    
def fetch_source_data(structure, integration):
    try:
        fetch_structure = json.loads(structure)
        host, port, user, password = get_mysql_credentials(integration.source.sql_dialect, integration.source)
        file_name = 'data_properties.json'
        if os.path.isfile(file_name):
            os.remove(file_name)
        with open(file_name, 'w+') as json_file:
            json.dump(fetch_structure, json_file)
        fetch_data_from_mysql(host, port, user, password)
        return True
    except Exception as e:
        print(str(e))
        return False

def insert_data_into_target(structure, integration):
    try:
        host, port, user, password = get_postgresql_credentials(integration.destination.sql_dialect, integration.destination)
        insertion_status = insert_data_into_postgres_target(host, port, user, password)
        return insertion_status
    except Exception as e:
        print(str(e))
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
        return Response(data={'success': 'Structure has been replicated successfully.'}, status=status.HTTP_200_OK)


class LoadDataIntoTarget(APIView):

    def post(self, request, format=None):
        integration_id = request.data.get('integration')
        if not integration_id:
            return Response(data={'error': 'Please provide integration'}, status=status.HTTP_400_BAD_REQUEST)
        integration = None
        try:
            integration = Integration.objects.get(pk=integration_id)
        except Exception as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        fetch_data_structure = request.data.get('structure')
        if not fetch_data_structure:
            return Response(data={'error': 'Please provide second structure required for data fetching from source'}, status=status.HTTP_400_BAD_REQUEST)
        data = fetch_source_data(fetch_data_structure, integration)
        if not data:
            return Response(data={'error': 'Something went wrong while fetching data from source'}, status=status.HTTP_400_BAD_REQUEST)
        data = insert_data_into_target(fetch_data_structure, integration)
        if not data:
            return Response(data={'error': 'Something went wrong while inserting data into target'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'success': 'Data has been inserted successfully into Target'}, status=status.HTTP_200_OK)


def load_data_from_api(source_creds, target_creds):
    endpoint = source_creds.get('endpoint')
    if not endpoint:
        return False
    try:
        custom_endpoint = endpoint.split('//')
        custom_endpoint[0] = '{}//{}:{}@'.format(custom_endpoint[0], source_creds.get('username', ''), source_creds.get('password', ''))
        custom_endpoint = ''.join(custom_endpoint)
        res = requests.get(url=custom_endpoint)
        res_data = json.loads(res.text)
        if 'error' in res_data[0].keys():
            return False
        data = load_data_into_target_db(target_creds['host'], target_creds['port'], target_creds['user'], target_creds['password'], res_data)
        return data
    except Exception as e:
        return False


class LoadAPIDataToTarget(APIView):

    def post(self, request, format=None):
        integration_id = request.data.get('integration')
        if not integration_id:
            return Response(data={'error': 'Please provide integration'}, status=status.HTTP_400_BAD_REQUEST)
        integration = None
        try:
            integration = Integration.objects.get(pk=integration_id)
        except Exception as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        source_creds = json.loads(integration.source.credential)
        target_creds = json.loads(integration.destination.credential)
        data = load_data_from_api(source_creds, target_creds)
        if not data:
            return Response(data={'error': 'Something went wrong while replicating DB structure.'}, 
            status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'success': 'Data has been inserted successfully into Target'}, status=status.HTTP_200_OK)

class TransformData(APIView):

    def post(self, request, format=None):
        integration_id = request.data.get('integration')
        if not integration_id:
            return Response(data={'error': 'Please provide integration'}, status=status.HTTP_400_BAD_REQUEST)
        integration = None
        try:
            integration = Integration.objects.get(pk=integration_id)
        except Exception as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        query = request.data.get('query', None)
        if not query:
            return Response(data={'error': 'There is not any query to execute'}, status=status.HTTP_400_BAD_REQUEST)
        target_name = integration.destination.sql_dialect.name
        creds = None
        if target_name.lower() == 'mysql':
            creds = json.loads(integration.destination.credential)
        if target_name.lower() == 'postgresql':
            creds = json.loads(integration.destination.credential)
            test = test_postgresql_connection(creds['host'], creds['port'], creds['user'], creds['password'])
            if not test:
                return Response(data={'error': 'Unable to establish connection with Target'}, status=status.HTTP_400_BAD_REQUEST)
        data = _do_transformation(creds['host'], creds['port'], creds['user'], creds['password'], query)
        return Response(data=data, status=status.HTTP_200_OK)
