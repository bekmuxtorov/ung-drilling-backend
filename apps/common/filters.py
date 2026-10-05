import django_filters
from .models import AuditLog, AuditAction


class AuditLogFilter(django_filters.FilterSet):
    """
    Audit loglarini qidirish va filtrlash uchun FilterSet.
    """
    user = django_filters.NumberFilter(field_name='user_id')
    username = django_filters.CharFilter(lookup_expr='icontains')
    ip_address = django_filters.CharFilter(lookup_expr='icontains')
    mac_address = django_filters.CharFilter(lookup_expr='icontains')
    action = django_filters.ChoiceFilter(choices=AuditAction.choices)
    app_label = django_filters.CharFilter(lookup_expr='exact')
    model_name = django_filters.CharFilter(lookup_expr='icontains')
    object_id = django_filters.CharFilter(lookup_expr='exact')
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = AuditLog
        fields = [
            'user',
            'username',
            'ip_address',
            'mac_address',
            'action',
            'app_label',
            'model_name',
            'object_id',
            'date_from',
            'date_to',
        ]
