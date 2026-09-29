from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DerrickErectionOperationViewSet,
    OperationStageViewSet,
    DailyWorkDescriptionViewSet,
    DailyTransportItemViewSet,
)

router = DefaultRouter()
router.register(r'derrick-erection-operations', DerrickErectionOperationViewSet, basename='derrick-erection-operation')
router.register(r'operation-stages', OperationStageViewSet, basename='operation-stage')
router.register(r'daily-works', DailyWorkDescriptionViewSet, basename='daily-work')
router.register(r'daily-transports', DailyTransportItemViewSet, basename='daily-transport')

urlpatterns = [
    path('', include(router.urls)),
]
