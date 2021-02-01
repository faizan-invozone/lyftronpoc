from django.shortcuts import render
from rest_framework import viewsets
from job.models import Job, JobStagingTable
from job.serializers import JobSerializer


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.all()

    def create(self, request):
        job = super(JobViewSet, self).create(request)
        query = request.data.get('job_action', None)
        table_names = query.split(" ")[-1:]
        table_names = ''.join(x for x in table_names)
        for table_name in table_names:
            job_table = JobStagingTable(name=table_name, job_id=job.data['id'])
            job_table.save()
        return job
