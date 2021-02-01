from rest_framework import serializers
from job_scheduler.models import JobScheduler


class JobSchedulerSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobScheduler
        fields = '__all__'
