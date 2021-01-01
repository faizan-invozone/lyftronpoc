from rest_framework import serializers
from databaseconnection.models import DatabaseConnecion, Integration


class DatabaseConnectionSerializer(serializers.ModelSerializer):
    credential = serializers.JSONField()
    class Meta:
        model = DatabaseConnecion
        fields = ['name', 'sql_dialect', 'credential', 'connection_type']
        lookup_field = 'connection_type'


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = '__all__'
