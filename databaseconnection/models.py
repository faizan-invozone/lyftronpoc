from django.db import models
from sqldialect.models import SqlDialect


CONNECTION_TYPE = [
    ('Source', 'source'),
    ('Target', 'target'),
]
class DatabaseConnecion(models.Model):
    name = models.CharField(max_length=100)
    sql_dialect = models.ForeignKey(SqlDialect, on_delete=models.CASCADE)
    credential = models.TextField()
    connection_type = models.CharField(max_length=10, choices=CONNECTION_TYPE, default='source')


class Integration(models.Model):
    name = models.CharField(max_length=100)
    source = models.ForeignKey(SqlDialect, on_delete=models.CASCADE, related_name='source', related_query_name='source')
    destination = models.ForeignKey(SqlDialect, on_delete=models.CASCADE, related_name='destination', related_query_name='destination')
