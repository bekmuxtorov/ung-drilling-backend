import django_filters
from .models import (
    DerrickErectionOperation,
    OperationStage,
    DailyWorkDescription,
    DailyTransportItem,
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
