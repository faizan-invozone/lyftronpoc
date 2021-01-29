from django.urls import path, include
from .views import ListMetaData, ReplicateMetaData,\
     LoadDataIntoTarget, LoadAPIDataToTarget, TransformData, \
        GetIntegrationMetaData, ReplicateMetaDataETL, LoadDataIntoStagingETL, \
            TransformDataETL, LoadDataIntoTargetETL



urlpatterns = [
    path('api/v1/get-metadata', ListMetaData.as_view()),
    path('api/v1/replicate-metadata', ReplicateMetaData.as_view()),
    path('api/v1/replicate-metadata-etl', ReplicateMetaDataETL.as_view()),
    path('api/v1/load-data', LoadDataIntoTarget.as_view()),
    path('api/v1/load-data-etl', LoadDataIntoStagingETL.as_view()),
    path('api/v1/load-api-data/', LoadAPIDataToTarget.as_view()),
    path('api/v1/transform-target/', TransformData.as_view()),
    path('api/v1/transform-staging/', TransformDataETL.as_view()),
    path('api/v1/integration-metadata', GetIntegrationMetaData.as_view()),
    path('api/v1/load-data-target-etl', LoadDataIntoTargetETL.as_view()),
]
