from django.urls import path, include
from rest_framework.routers import DefaultRouter
from sqldialect.views import SqlDialectViewSet, SourceDatatypeViewSet, TargetDatatypeViewSet, DatatypeMappingViewSet


router = DefaultRouter()
router.register(r'sqldialects', SqlDialectViewSet, basename='sqldialect')
router.register(r'source-datatypes', SourceDatatypeViewSet, basename='sourcedatatype')
router.register(r'target-datatypes', TargetDatatypeViewSet, basename='targetdatatype')
router.register(r'datatype-mappings', DatatypeMappingViewSet, basename='datatypemapping')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
