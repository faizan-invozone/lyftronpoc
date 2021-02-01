from django.shortcuts import render
from job_scheduler.serializers import JobSchedulerSerializer
from job_scheduler.models import JobScheduler
from rest_framework import viewsets


class JobSchedulerViewSet(viewsets.ModelViewSet):
    serializer_class = JobSchedulerSerializer
    queryset = JobScheduler.objects.all()
