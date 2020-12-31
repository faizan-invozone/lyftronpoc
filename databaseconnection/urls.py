from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatabaseConnectionViewSet, IntegrationViewSet, TestConnection


router = DefaultRouter()
router.register(r'connections', DatabaseConnectionViewSet, basename='sqldialect')
router.register(r'integrations', IntegrationViewSet, basename='sourcedatatype')

urlpatterns = [
    path(r'api/v1/', include(router.urls)),
    path(r'api/v1/test-connection', TestConnection.as_view())
]
