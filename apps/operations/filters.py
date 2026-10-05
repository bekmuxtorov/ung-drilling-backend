import django_filters
from .models import (
    DerrickErectionOperation,
    OperationStage,
    DailyWorkDescription,
    DailyTransportItem,
    DrillingBPA,
    WellDesign,
    WellDesignInLength,
    DepthsLayersLength,
    DailyWorkDescriptionBPA,
    AvailableResourcesBPA,
)



class DerrickErectionOperationFilter(django_filters.FilterSet):
    from_well_number = django_filters.CharFilter(lookup_expr='icontains')
    to_well_number = django_filters.CharFilter(lookup_expr='icontains')
    min_completion = django_filters.NumberFilter(field_name='completion_percentage', lookup_expr='gte')
    max_completion = django_filters.NumberFilter(field_name='completion_percentage', lookup_expr='lte')
    drilling_date_from = django_filters.DateFilter(field_name='expected_drilling_date', lookup_expr='gte')
    drilling_date_to = django_filters.DateFilter(field_name='expected_drilling_date', lookup_expr='lte')

    class Meta:
        model = DerrickErectionOperation
        fields = [
            'enterprise',
            'drilling_rig_type',
            'from_area',
            'from_well_number',
            'to_area',
            'to_well_number',
            'foreman',
            'min_completion',
            'max_completion',
            'drilling_date_from',
            'drilling_date_to',
        ]


class OperationStageFilter(django_filters.FilterSet):
    class Meta:
        model = OperationStage
        fields = [
            'operation',
            'stage_type',
        ]


class DailyWorkDescriptionFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = DailyWorkDescription
        fields = [
            'derrick_erection_operation',
            'date_from',
            'date_to',
        ]


class DailyTransportItemFilter(django_filters.FilterSet):
    class Meta:
        model = DailyTransportItem
        fields = [
            'daily_work_description',
            'transport_type',
        ]


class DrillingBPAFilter(django_filters.FilterSet):
    number = django_filters.CharFilter(lookup_expr='icontains')
    well_number = django_filters.CharFilter(lookup_expr='icontains')
    enterprise = django_filters.NumberFilter(field_name='enterprise_id')
    employee = django_filters.NumberFilter(field_name='employee_id')
    area = django_filters.NumberFilter(field_name='area_id')
    machine_type = django_filters.NumberFilter(field_name='machine_type_id')
    start_date_from = django_filters.DateTimeFilter(field_name='drilling_start_date', lookup_expr='gte')
    start_date_to = django_filters.DateTimeFilter(field_name='drilling_start_date', lookup_expr='lte')
    depth_min = django_filters.NumberFilter(field_name='depth_plan', lookup_expr='gte')
    depth_max = django_filters.NumberFilter(field_name='depth_plan', lookup_expr='lte')

    class Meta:
        model = DrillingBPA
        fields = [
            'number',
            'well_number',
            'enterprise',
            'employee',
            'area',
            'machine_type',
            'start_date_from',
            'start_date_to',
            'depth_min',
            'depth_max',
        ]


class WellDesignFilter(django_filters.FilterSet):
    drilling_bpa = django_filters.NumberFilter(field_name='drilling_bpa_id')
    type = django_filters.CharFilter()

    class Meta:
        model = WellDesign
        fields = ['drilling_bpa', 'type']


class WellDesignInLengthFilter(django_filters.FilterSet):
    drilling_bpa = django_filters.NumberFilter(field_name='drilling_bpa_id')
    type = django_filters.CharFilter()
    date_from = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='lte')

    class Meta:
        model = WellDesignInLength
        fields = ['drilling_bpa', 'type', 'date_from', 'date_to']


class DepthsLayersLengthFilter(django_filters.FilterSet):
    drilling_bpa = django_filters.NumberFilter(field_name='drilling_bpa_id')
    layer = django_filters.NumberFilter(field_name='layer_id')

    class Meta:
        model = DepthsLayersLength
        fields = ['drilling_bpa', 'layer']


class DailyWorkDescriptionBPAFilter(django_filters.FilterSet):
    drilling_bpa = django_filters.NumberFilter(field_name='drilling_bpa_id')
    report_date = django_filters.DateFilter()
    date_from = django_filters.DateFilter(field_name='report_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='report_date', lookup_expr='lte')

    class Meta:
        model = DailyWorkDescriptionBPA
        fields = ['drilling_bpa', 'report_date', 'date_from', 'date_to']


class AvailableResourcesBPAFilter(django_filters.FilterSet):
    drilling_bpa = django_filters.NumberFilter(field_name='drilling_bpa_id')
    resources = django_filters.NumberFilter(field_name='resources_id')
    unit = django_filters.NumberFilter(field_name='unit_id')

    class Meta:
        model = AvailableResourcesBPA
        fields = ['drilling_bpa', 'resources', 'unit']

