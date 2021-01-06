from django.shortcuts import render
from rest_framework import viewsets
from sqldialect.models import SqlDialect, SourceDatatype, TargetDatatype, DatatypeMapping
from sqldialect.serializers import SqlDialectSerializer, SourceDatatypeSerializer, TargetDatatypeSerializer, DatatypeMappingSerializer


class SqlDialectViewSet(viewsets.ModelViewSet):
    serializer_class = SqlDialectSerializer
    queryset = SqlDialect.objects.all()


class SourceDatatypeViewSet(viewsets.ModelViewSet):
    serializer_class = SourceDatatypeSerializer
    queryset = SourceDatatype.objects.all()


class TargetDatatypeViewSet(viewsets.ModelViewSet):
    serializer_class = TargetDatatypeSerializer
    queryset = TargetDatatype.objects.all()


class DatatypeMappingViewSet(viewsets.ModelViewSet):
    serializer_class = DatatypeMappingSerializer
    queryset = DatatypeMapping.objects.all()
