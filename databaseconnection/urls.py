from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatabaseConnectionViewSet, IntegrationViewSet


router = DefaultRouter()
router.register(r'connections', DatabaseConnectionViewSet, basename='sqldialect')
router.register(r'integrations', IntegrationViewSet, basename='sourcedatatype')

urlpatterns = [
    path(r'api/v1/', include(router.urls)),
]
