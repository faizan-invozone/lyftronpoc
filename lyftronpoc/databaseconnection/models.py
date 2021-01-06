from django.db import models
from sqldialect.models import SqlDialect


CONNECTION_TYPE = [
    ('source', 'Source'),
    ('target', 'Target'),
]
class DatabaseConnecion(models.Model):
    name = models.CharField(max_length=100)
    sql_dialect = models.ForeignKey(SqlDialect, on_delete=models.CASCADE)
    credential = models.TextField()
    connection_type = models.CharField(max_length=10, choices=CONNECTION_TYPE, default='source')
    
    def __str__(self):
        return self.name
    

class Integration(models.Model):
    name = models.CharField(max_length=100)
    source = models.ForeignKey(DatabaseConnecion, on_delete=models.CASCADE, related_name='source', related_query_name='source')
    destination = models.ForeignKey(DatabaseConnecion, on_delete=models.CASCADE, related_name='destination', related_query_name='destination')

    def __str__(self):
        return self.name
    