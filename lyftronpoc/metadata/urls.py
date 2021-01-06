from django.urls import path, include
from .views import ListMetaData, ReplicateMetaData


urlpatterns = [
    path('api/v1/get-metadata', ListMetaData.as_view()),
    path('api/v1/replicate-metadata', ReplicateMetaData.as_view()),
]
