from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from databaseconnection.models import Integration
import json
import os
import requests
from utils.mysql_meta import mysql_meta_
from utils.postgresql_target import replicate_to_target, replicate_to_staging_and_target
from utils.fetch_data import fetch_data_from_mysql
from utils.insert_into_target import insert_data_into_postgres_target
from utils.get_api_metadata import load_data_into_target_db
from utils.postgresql_target import test_postgresql_connection
from utils.tranf_elt import _do_transformation
from utils.CDC_elt import MYSQL_SETTINGS
from utils.CDC_action import apply_cdc
from metadata.models import VirtualDatabase, VirtualSchema, VirtualTable, VirtualColumn, VirtualColumnAttribute
from multiprocessing import Process
from utils.etl_transformation import insert_into_target_etl
from job.models import Job, JobStagingTable


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


def replicate_db_structure(integration, structure, etl=None):
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
        if not etl:
            replicate_to_target(host, port, user, password, structure)
        else:
            replicate_to_staging_and_target(host, port, user, password, structure)
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

def insert_data_into_target(structure, integration, etl=None):
    try:
        host, port, user, password = get_postgresql_credentials(integration.destination.sql_dialect, integration.destination)
        insertion_status = insert_data_into_postgres_target(host, port, user, password, etl)
        return insertion_status
    except Exception as e:
        print(str(e))
        return False
    
def _store_metadata(structure, integration):
    metadata = json.loads(structure)
    metadata_dict = metadata.get('stream_data', None)
    if not metadata_dict:
        return False
    db_name = None
    virtual_database = None
    virtual_schema = None
    for metadata in metadata_dict:
        db, table_name = metadata['tap_stream_id'].split('-')
        if db_name != db:
            db_name = db
            virtual_database = VirtualDatabase.objects.filter(name=db_name, integration_id=integration.id)
            if not virtual_database:
                virtual_database = VirtualDatabase(name=db_name, integration_id=integration.id)
                virtual_database.save()
            else:
                virtual_database = virtual_database[0]
            schema_name = 'public'
            virtual_schema = VirtualSchema.objects.filter(name=schema_name, virtual_database_id=virtual_database.id)
            if not virtual_schema:
                virtual_schema = VirtualSchema(name=schema_name, virtual_database_id=virtual_database.id)
                virtual_schema.save()
            else:
                virtual_schema = virtual_schema[0]
        if not virtual_schema:
            continue
        virtual_table = VirtualTable.objects.filter(name=table_name, virtual_schema_id=virtual_schema.id)
        if not virtual_table:
            virtual_table = VirtualTable(name=table_name, virtual_schema_id=virtual_schema.id)
            virtual_table.save()
        else:
            virtual_table = virtual_table[0]
        actual_meta = metadata.get('metadata', None)
        if not actual_meta:
            continue
        properties = actual_meta.get('properties', None)
        for column_name, column_attributes in properties.items():
            virtual_column = VirtualColumn.objects.filter(name=column_name, virtual_table_id=virtual_table.id)
            if not virtual_column:
                virtual_column = VirtualColumn(name=column_name, virtual_table_id=virtual_table.id)
                virtual_column.save()
            else:
                virtual_column = virtual_column[0]
            for attribute_name, attribute_value in column_attributes.items():
                virtual_column_attribute = VirtualColumnAttribute.objects.filter(
                    name=attribute_name,
                    value=attribute_value,
                    virtual_column_id=virtual_column.id
                )
                if not virtual_column_attribute:
                    virtual_column_attribute = VirtualColumnAttribute(
                        name=attribute_name,
                        value=attribute_value,
                        virtual_column_id=virtual_column.id
                    )
                    virtual_column_attribute.save()
    return True

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
        _store_metadata(structure, integration)
        return Response(data={'success': 'Structure has been replicated successfully.'}, status=status.HTTP_200_OK)

def _overwrite_source_config(host, port, user, password, integration_id=None):
    file_name = 'config_source.json'
    with open(file_name,"r") as json_file:
        data = json.load(json_file)
        data['host'] = host
        data['port'] = port
        data['user'] = user
        data['password'] = password
        if integration_id:
            data['integration_id'] = integration_id
    with open(file_name, "w") as jsonFile:
        json.dump(data, jsonFile)

def _apply_CDC(integration, etl=None):
    host, port, user, password = get_mysql_credentials(integration.source.sql_dialect, integration.source)
    _overwrite_source_config(host, port, user, password, integration.id)
    host, port, user, password = get_postgresql_credentials(integration.destination.sql_dialect, integration.destination)
    virtual_db = VirtualDatabase.objects.filter(integration_id=integration.id)
    if not virtual_db:
        return False
    virtual_db = virtual_db[0]
    process = Process(
        name='{}_process'.format(virtual_db), target=apply_cdc, 
        args=(host, port, user, password, virtual_db.name, etl)
    )
    process.start()
    return True

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
        _apply_CDC(integration)
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
        virtual_db = VirtualDatabase.objects.filter(integration_id=integration.id)
        if not virtual_db:
            return Response(data={'error': 'Database is not selected.'}, status=status.HTTP_400_BAD_REQUEST)
        virtual_db = virtual_db[0]
        print(creds['host'], creds['port'], creds['user'], creds['password'], virtual_db.name, query)
        data = _do_transformation(creds['host'], creds['port'], creds['user'], creds['password'], virtual_db.name, query)
        return Response(data=data, status=status.HTTP_200_OK)


class GetIntegrationMetaData(APIView):

    def post(self, request, format=None):
        integration_id = request.data.get('integration')
        if not integration_id:
            return Response(data={'error': 'Please provide integration'}, status=status.HTTP_400_BAD_REQUEST)
        integration = None
        try:
            integration = Integration.objects.get(pk=integration_id)
        except Exception as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        data = []
        databases = integration.virtualdatabase_set.all()
        for database in databases:
            res_data = {'database': database.name}
            schemas = database.virtualschema_set.all()
            for schema in schemas:
                res_data['schema'] = schema.name
                tables = schema.virtualtable_set.all()
                res_data['table'] = []
                for table in tables:
                    res_table = {'name': table.name}
                    columns = table.virtualcolumn_set.all()
                    res_table['column'] = []
                    for column in columns:
                        res_table['column'].append({'name': column.name})
                    res_data['table'].append(res_table)
        return Response(data={'data': res_data}, status=status.HTTP_200_OK)


class TransformETLData(APIView):

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
        virtual_db = VirtualDatabase.objects.filter(integration_id=integration.id)
        if not virtual_db:
            return Response(data={'error': 'Database is not selected.'}, status=status.HTTP_400_BAD_REQUEST)
        virtual_db = virtual_db[0]
        print(creds['host'], creds['port'], creds['user'], creds['password'], virtual_db.name, query)
        data = _do_transformation(creds['host'], creds['port'], creds['user'], creds['password'], virtual_db.name, query)
        return Response(data=data, status=status.HTTP_200_OK)


class ReplicateMetaDataETL(APIView):

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
        replication = replicate_db_structure(integration, structure, True)
        if not replication:
            return Response(data={'error': 'Something went wrong while replicating DB structure.'}, 
            status=status.HTTP_400_BAD_REQUEST)
        _store_metadata(structure, integration)
        return Response(data={'success': 'Structure has been replicated successfully.'}, status=status.HTTP_200_OK)


class LoadDataIntoStagingETL(APIView):

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
        data = insert_data_into_target(fetch_data_structure, integration, True)
        if not data:
            return Response(data={'error': 'Something went wrong while inserting data into target'}, status=status.HTTP_400_BAD_REQUEST)
        _apply_CDC(integration, True)
        return Response(data={'success': 'Data has been inserted successfully into Target'}, status=status.HTTP_200_OK)


class TransformDataETL(APIView):

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
        virtual_db = VirtualDatabase.objects.filter(integration_id=integration.id)
        if not virtual_db:
            return Response(data={'error': 'Database is not selected.'}, status=status.HTTP_400_BAD_REQUEST)
        virtual_db = virtual_db[0]
        print(creds['host'], creds['port'], creds['user'], creds['password'], virtual_db.name, query)
        data = _do_transformation(creds['host'], creds['port'], creds['user'], creds['password'], virtual_db.name, query, True)
        return Response(data=data, status=status.HTTP_200_OK)


class LoadDataIntoTargetETL(APIView):
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
        creds = json.loads(integration.destination.credential)
        virtual_db = VirtualDatabase.objects.filter(integration_id=integration.id)
        if not virtual_db:
            return Response(data={'error': 'Database is not selected.'}, status=status.HTTP_400_BAD_REQUEST)
        virtual_db = virtual_db[0]
        creds['database'] = virtual_db.name
        insert_into_target_etl(creds, query)
        return Response(data={'data': 'Success'}, status=status.HTTP_200_OK)


class IntegrationActions(APIView):

    def post(self, request, format=None):
        integration_id = request.data.get('integration')
        if not integration_id:
            return Response(data={'error': 'Please provide integration'}, status=status.HTTP_400_BAD_REQUEST)
        integration = None
        try:
            integration = Integration.objects.get(pk=integration_id)
        except Exception as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        table_name = request.data.get('table_name', None)
        if not table_name:
            return Response(data={'error': 'Please provide table name to complete the action'}, status=status.HTTP_400_BAD_REQUEST)
        jobs = Job.objects.filter(integration_id=integration_id, jobstagingtable__name=table_name)
        data = []
        for job in jobs:
            data.append({'job_action': job.job_action})
        return Response(data={'data': data}, status=status.HTTP_200_OK)
