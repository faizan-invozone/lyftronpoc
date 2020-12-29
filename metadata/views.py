from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from databaseconnection.models import Integration


class ListMetaData(APIView):
    
    def get(self, request, format=None):
        integration_id = request.data.get('integration', None)
        if not integration_id:
            return Response(data={'error': 'Please provide integration ID'})
        integration = Integration.objects.filter(pk=integration_id)
        if integration:
            integration = integration[0]
        return Response(data={'data': 'integration found'})
