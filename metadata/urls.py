from django.urls import path, include
from .views import ListMetaData


urlpatterns = [
    path('api/v1/get-metadata', ListMetaData.as_view()),
]
