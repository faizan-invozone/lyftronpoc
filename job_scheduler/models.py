from django.db import models
from job.models import Job


REPETITION_TYPE = [
    ('minutes', 'Minutes'),
    ('hours', 'Hours'),
    ('day_of_month', 'Day of Month'),
    ('month', 'Month'),
    ('day_of_week', 'Day of Week')
]


class JobScheduler(models.Model):
    name = models.CharField(max_length=255)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    repetition_type = models.CharField(max_length=20, choices=REPETITION_TYPE, null=True, blank=True)
    repetition_value = models.CharField(max_length=255, null=True, blank=True)
