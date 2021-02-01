from django.db import models
from databaseconnection.models import Integration

class Job(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, null=True, blank=True)
    job_action = models.TextField()
