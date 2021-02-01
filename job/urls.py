from django.urls import path, include
from rest_framework.routers import DefaultRouter
from job.views import JobViewSet


router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='jobs')

urlpatterns = [
    path(r'api/v1/', include(router.urls)),
]
