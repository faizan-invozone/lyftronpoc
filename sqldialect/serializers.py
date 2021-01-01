from rest_framework import serializers
from .models import SqlDialect, SourceDatatype, TargetDatatype, DatatypeMapping


class SqlDialectSerializer(serializers.ModelSerializer):
    credential = serializers.JSONField()

    class Meta:
        model = SqlDialect
        fields = ['name', 'provider', 'credential']


class SourceDatatypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceDatatype
        fields = '__all__'


class TargetDatatypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetDatatype
        fields = '__all__'


class DatatypeMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatatypeMapping
        fields = '__all__'
