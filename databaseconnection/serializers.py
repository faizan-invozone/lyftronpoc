from rest_framework import serializers
from databaseconnection.models import DatabaseConnecion, Integration


class DatabaseConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseConnecion
        fields = '__all__'


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = '__all__'
