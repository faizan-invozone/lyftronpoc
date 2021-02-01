from django.urls import path, include
from rest_framework.routers import DefaultRouter
from job_scheduler.views import JobSchedulerViewSet


router = DefaultRouter()
router.register(r'schedulers', JobSchedulerViewSet, basename='job-schedulers')

urlpatterns = [
    path(r'api/v1/', include(router.urls)),
]
