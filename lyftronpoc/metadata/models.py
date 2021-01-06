from django.db import models
from sqldialect.models import DatatypeMapping
from databaseconnection.models import Integration


class VirtualDatabase(models.Model):
    name = models.CharField(max_length=500)
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE)


class VirtualSchema(models.Model):
    name = models.CharField(max_length=500)
    virtual_database = models.ForeignKey(VirtualDatabase, on_delete=models.CASCADE)


class VirtualTable(models.Model):
    name = models.CharField(max_length=100)
    virtual_schema = models.ForeignKey(VirtualSchema, on_delete=models.CASCADE)


class ViratualColumn(models.Model):
    name = models.CharField(max_length=500)
    actual_name = models.CharField(max_length=500)
    length = models.CharField(max_length=20)
    mapping = models.ForeignKey(DatatypeMapping, on_delete=models.CASCADE)
    virtual_table = models.ForeignKey(VirtualTable, on_delete=models.CASCADE)


class Pipeline(models.Model):
    name = models.CharField(max_length=500)
    pipeline_sql = models.TextField()
