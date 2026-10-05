from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DerrickErectionOperationViewSet,
    OperationStageViewSet,
    DailyWorkDescriptionViewSet,
    DailyTransportItemViewSet,
    DrillingBPAViewSet,
    WellDesignViewSet,
    WellDesignInLengthViewSet,
    DepthsLayersLengthViewSet,
    DailyWorkDescriptionBPAViewSet,
    AvailableResourcesBPAViewSet,
)

router = DefaultRouter()
router.register(r'derrick-erection-operations', DerrickErectionOperationViewSet, basename='derrick-erection-operation')
router.register(r'operation-stages', OperationStageViewSet, basename='operation-stage')
router.register(r'daily-works', DailyWorkDescriptionViewSet, basename='daily-work')
router.register(r'daily-transports', DailyTransportItemViewSet, basename='daily-transport')
router.register(r'drilling-bpas', DrillingBPAViewSet, basename='drilling-bpa')
router.register(r'well-designs', WellDesignViewSet, basename='well-design')
router.register(r'well-designs-in-length', WellDesignInLengthViewSet, basename='well-design-in-length')
router.register(r'depths-layers-lengths', DepthsLayersLengthViewSet, basename='depths-layers-length')
router.register(r'daily-works-bpa', DailyWorkDescriptionBPAViewSet, basename='daily-work-bpa')
router.register(r'available-resources-bpa', AvailableResourcesBPAViewSet, basename='available-resources-bpa')

urlpatterns = [
    path('', include(router.urls)),
]

