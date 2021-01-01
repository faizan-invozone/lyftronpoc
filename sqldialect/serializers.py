from rest_framework import serializers
from .models import SqlDialect, SourceDatatype, TargetDatatype, DatatypeMapping
import json


class JSONSerializerField(serializers.Field):

    def to_internal_value(self, data):
        return json.dumps(data)

    def to_representation(self, value):
        return json.loads(value)


class SqlDialectSerializer(serializers.ModelSerializer):
    credential = JSONSerializerField()

    class Meta:
        model = SqlDialect
        fields = ['id', 'name', 'provider', 'credential']


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
