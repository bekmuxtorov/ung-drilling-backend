import django_filters
from .models import (
    Enterprise,
    DrillingRigType,
    Region,
    Area,
    Foreman,
    TransportType,
    Position,
    Employee,
    MachineType,
    DepthsLayers,
    Resources,
    Unit,
)



class EnterpriseFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Enterprise
        fields = ['name']


class DrillingRigTypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = DrillingRigType
        fields = ['name']


class RegionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Region
        fields = ['name']


class AreaFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    region = django_filters.ModelChoiceFilter(queryset=Region.objects.all())
    region_id = django_filters.NumberFilter(field_name='region__id')

    class Meta:
        model = Area
        fields = ['name', 'region', 'region_id']


class ForemanFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Foreman
        fields = ['name', 'phone']


class TransportTypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = TransportType
        fields = ['name']


class PositionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Position
        fields = ['name']


class EmployeeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    phone_number = django_filters.CharFilter(lookup_expr='icontains')
    position = django_filters.ModelChoiceFilter(queryset=Position.objects.all())
    position_id = django_filters.NumberFilter(field_name='position__id')

    class Meta:
        model = Employee
        fields = ['name', 'phone_number', 'position', 'position_id']


class MachineTypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = MachineType
        fields = ['name']


class DepthsLayersFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = DepthsLayers
        fields = ['name']


DepthLayerFilter = DepthsLayersFilter


class ResourcesFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Resources
        fields = ['name']


ResourceFilter = ResourcesFilter


class UnitFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Unit
        fields = ['name']

