from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import AuditLog
from .serializers import AuditLogSerializer
from .filters import AuditLogFilter


@extend_schema_view(
    list=extend_schema(
        tags=["Audit loglari (Audit Trail)"],
        summary="Barcha audit loglari ro'yxati",
        description=(
            "Tizimdagi barcha o'zgarishlar (yaratish, tahrirlash, o'chirish) jurnali. "
            "Qaysi foydalanuvchi, qaysi IP manzil, qaysi MAC ID/qurilma orqali qanday o'zgarish qilgani "
            "(eski va yangi qiymatlar, diff formatida) ko'rsatiladi. "
            "Foydalanuvchi, model, sana oraliqlari, harakat turi bo'yicha filtrlash imkoniyati mavjud."
        )
    ),
    retrieve=extend_schema(
        tags=["Audit loglari (Audit Trail)"],
        summary="Bitta audit logi ma'lumotlari",
        description="Muayyan o'zgarish qaydnomasining to'liq tafsilotlari (barcha eski/yangi qiymatlar va parametrlar)."
    ),
)
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Xavfsizlik va ma'lumotlar yaxlitligini ta'minlash uchun Audit loglari
    faqat o'qish (Read-Only) rejimida taqdim etiladi.
    Tizim loglari API orqali tahrirlanishi yoki o'chirilishi qat'iyan taqiqlanadi (Append-Only).
    """
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuditLogFilter
    search_fields = [
        'object_repr',
        'username',
        'model_name',
        'ip_address',
        'mac_address',
        'object_id',
    ]
    ordering_fields = ['id', 'created_at', 'model_name', 'action', 'username']
    ordering = ['-created_at']
