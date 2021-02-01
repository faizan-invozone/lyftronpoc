from django.shortcuts import render
from rest_framework import viewsets
from job.models import Job
from job.serializers import JobSerializer


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.all()
