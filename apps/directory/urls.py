from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EnterpriseViewSet,
    DrillingRigTypeViewSet,
    RegionViewSet,
    AreaViewSet,
    ForemanViewSet,
    TransportTypeViewSet,
    PositionViewSet,
    EmployeeViewSet,
    OperationStageTypeView,
)

router = DefaultRouter()
router.register(r'enterprises', EnterpriseViewSet, basename='enterprise')
router.register(r'drilling-rig-types', DrillingRigTypeViewSet, basename='drilling-rig-type')
router.register(r'regions', RegionViewSet, basename='region')
router.register(r'areas', AreaViewSet, basename='area')
router.register(r'foremen', ForemanViewSet, basename='foreman')
router.register(r'transport-types', TransportTypeViewSet, basename='transport-type')
router.register(r'positions', PositionViewSet, basename='position')
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('operation-stages/', OperationStageTypeView.as_view(), name='operation-stages'),
    path('', include(router.urls)),
]
