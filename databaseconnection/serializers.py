from rest_framework import serializers
from databaseconnection.models import DatabaseConnecion, Integration
import json


class JSONSerializerField(serializers.Field):

    def to_internal_value(self, data):
        return json.dumps(data)

    def to_representation(self, value):
        return json.loads(value)


class DatabaseConnectionSerializer(serializers.ModelSerializer):
    credential = JSONSerializerField()
    class Meta:
        model = DatabaseConnecion
        fields = ['id', 'name', 'sql_dialect', 'credential', 'connection_type']
        lookup_field = 'connection_type'


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = '__all__'
