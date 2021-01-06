from rest_framework import serializers
from metadata.models import VirtualDatabase, VirtualSchema, VirtualTable, ViratualColumn


class VirtualDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualDatabase
        fields = '__all__'


class VirtualSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualSchema
        fields = '__all__'


class VirtualTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualTable
        fields = '__all__'


class VirtualColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViratualColumn
        fields = '__all__'
