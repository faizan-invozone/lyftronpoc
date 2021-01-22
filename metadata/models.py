from django.db import models
from sqldialect.models import DatatypeMapping
from databaseconnection.models import Integration


class VirtualDatabase(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE)


class VirtualSchema(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    virtual_database = models.ForeignKey(VirtualDatabase, on_delete=models.CASCADE)


class VirtualTable(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    virtual_schema = models.ForeignKey(VirtualSchema, on_delete=models.CASCADE)


class ViratualColumn(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    # actual_name = models.CharField(max_length=500)
    # length = models.CharField(max_length=20, null=True, blank=True)
    # is_null = models.CharField(max_length=20, null=True, blank=True)
    # mapping = models.ForeignKey(DatatypeMapping, on_delete=models.CASCADE, null=True, blank=True)
    virtual_table = models.ForeignKey(VirtualTable, on_delete=models.CASCADE)

class VirtualColumnAttribute(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    value = models.CharField(max_length=255, null=True, blank=True)
    virtual_column = models.ForeignKey(ViratualColumn, on_delete=models.CASCADE)


class Pipeline(models.Model):
    name = models.CharField(max_length=500)
    pipeline_sql = models.TextField()
    
