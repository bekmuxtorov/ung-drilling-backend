from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import (
    DerrickErectionOperation,
    OperationStage,
    DailyWorkDescription,
    DailyTransportItem,
)
from .serializers import (
    DerrickErectionOperationSerializer,
    OperationStageSerializer,
    DailyWorkDescriptionSerializer,
    DailyTransportItemSerializer,
)
from .filters import (
    DerrickErectionOperationFilter,
    OperationStageFilter,
    DailyWorkDescriptionFilter,
    DailyTransportItemFilter,
)


@extend_schema_view(
    list=extend_schema(
        tags=["VBM Operatsiyalari (Vishka-montaj)"],
        summary="Barcha VBM operatsiyalari ro'yxati",
        description=(
            "Burg'ulash qurilmalarini ko'chirish va montaj qilish bo'yicha barcha operatsiyalar. "
            "Filtrlash, qidiruv (quduq raqami, maydon, usta ismi) va saralash imkoniyati mavjud. "
            "Bog'langan barcha ma'lumotnomalar (korxona, maydonlar, usta, uskuna) to'liq nested obyekt sifatida qaytariladi."
        )
    ),
    create=extend_schema(
        tags=["VBM Operatsiyalari (Vishka-montaj)"],
        summary="Yangi VBM operatsiyasini ro'yxatga olish",
        description="Yangi operatsiya kiritish. Barcha xorijiy kalitlar (enterprise, rig, areas, foreman) uchun ID yuboriladi."
    ),
    retrieve=extend_schema(
        tags=["VBM Operatsiyalari (Vishka-montaj)"],
        summary="Bitta VBM operatsiyasining to'liq ma'lumotlari",
        description="Operatsiyaning to'liq ko'rsatkichlari, unga biriktirilgan bosqichlar (stages) bilan birga qaytadi."
    ),
    update=extend_schema(
        tags=["VBM Operatsiyalari (Vishka-montaj)"],
        summary="VBM operatsiyasini to'liq yangilash",
        description="Operatsiya ko'rsatkichlarini to'liq tahrirlash (PUT)."
    ),
    partial_update=extend_schema(
        tags=["VBM Operatsiyalari (Vishka-montaj)"],
        summary="VBM operatsiyasini qisman yangilash",
        description="Operatsiya ko'rsatkichlarini (masalan, completion_percentage, delay_reason) qisman yangilash (PATCH)."
    ),
    destroy=extend_schema(
        tags=["VBM Operatsiyalari (Vishka-montaj)"],
        summary="VBM operatsiyasini o'chirish",
        description="Operatsiyani tizimdan o'chirish."
    ),
)
class DerrickErectionOperationViewSet(viewsets.ModelViewSet):
    # N+1 query optimizatsiyasi
    queryset = DerrickErectionOperation.objects.select_related(
        'enterprise',
        'drilling_rig_type',
        'from_area__region',
        'to_area__region',
        'foreman',
    ).prefetch_related('stages').all()
    serializer_class = DerrickErectionOperationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DerrickErectionOperationFilter
    search_fields = [
        'from_well_number',
        'to_well_number',
        'from_area__name',
        'to_area__name',
        'foreman__name',
        'work_description',
        'delay_reason',
    ]
    ordering_fields = [
        'id',
        'completion_percentage',
        'distance_km',
        'plan_days',
        'expected_drilling_date',
        'created_at',
    ]
    ordering = ['-id']

    @extend_schema(
        tags=["VBM Operatsiyalari (Vishka-montaj)"],
        summary="Ushbu operatsiyaga tegishli kunlik ish hisobotlari",
        description="Tanlangan VBM operatsiyasi bo'yicha kiritilgan barcha kunlik ish tavsiflari va jalb qilingan transportlar.",
        responses={200: DailyWorkDescriptionSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='daily-reports')
    def daily_reports(self, request, pk=None):
        operation = self.get_object()
        reports = operation.daily_works.prefetch_related('transport_items__transport_type').all()
        serializer = DailyWorkDescriptionSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        tags=["Operatsiya bosqichlari (Stages)"],
        summary="Operatsiya bosqichlari ro'yxati",
        description="Demontaj, Tashish va Montaj bosqichlari. `?operation=ID` parametri orqali muayyan operatsiyaga tegishli bosqichlarni olish mumkin."
    ),
    create=extend_schema(
        tags=["Operatsiya bosqichlari (Stages)"],
        summary="Yangi bosqich ma'lumotlarini qo'shish",
        description="Operatsiyaga yangi bosqich (reja/fakt kunlar, boshlanish/tugash sanalari) qo'shish."
    ),
    retrieve=extend_schema(
        tags=["Operatsiya bosqichlari (Stages)"],
        summary="Bitta bosqich ma'lumotlari",
        description="Bosqich tafsilotlari."
    ),
    update=extend_schema(
        tags=["Operatsiya bosqichlari (Stages)"],
        summary="Bosqichni to'liq yangilash",
        description="Bosqich ko'rsatkichlarini to'liq yangilash."
    ),
    partial_update=extend_schema(
        tags=["Operatsiya bosqichlari (Stages)"],
        summary="Bosqichni qisman yangilash",
        description="Bosqich ko'rsatkichlarini qisman yangilash (masalan, fact_days, fact_end_date)."
    ),
    destroy=extend_schema(
        tags=["Operatsiya bosqichlari (Stages)"],
        summary="Bosqichni o'chirish",
        description="Bosqichni tizimdan o'chirish."
    ),
)
class OperationStageViewSet(viewsets.ModelViewSet):
    queryset = OperationStage.objects.select_related('operation').all()
    serializer_class = OperationStageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OperationStageFilter
    search_fields = ['description']
    ordering_fields = ['id', 'plan_days', 'fact_days', 'plan_start_date', 'fact_start_date']
    ordering = ['id']


@extend_schema_view(
    list=extend_schema(
        tags=["Kunlik ish hisobotlari (Daily Works)"],
        summary="Kunlik ish hisobotlari ro'yxati",
        description="Kunlik ish tavsiflari va ularga biriktirilgan transport vositalari ro'yxati."
    ),
    create=extend_schema(
        tags=["Kunlik ish hisobotlari (Daily Works)"],
        summary="Yangi kunlik hisobot kiritish",
        description="Operatsiya bo'yicha yangi kunlik ish hisoboti yaratish."
    ),
    retrieve=extend_schema(
        tags=["Kunlik ish hisobotlari (Daily Works)"],
        summary="Bitta kunlik hisobot ma'lumotlari",
        description="Kunlik hisobot va unga biriktirilgan transportlar ro'yxati."
    ),
    update=extend_schema(
        tags=["Kunlik ish hisobotlari (Daily Works)"],
        summary="Kunlik hisobotni to'liq yangilash",
        description="Hisobotni to'liq yangilash."
    ),
    partial_update=extend_schema(
        tags=["Kunlik ish hisobotlari (Daily Works)"],
        summary="Kunlik hisobotni qisman yangilash",
        description="Hisobot matnini qisman yangilash."
    ),
    destroy=extend_schema(
        tags=["Kunlik ish hisobotlari (Daily Works)"],
        summary="Kunlik hisobotni o'chirish",
        description="Kunlik hisobotni tizimdan o'chirish."
    ),
)
class DailyWorkDescriptionViewSet(viewsets.ModelViewSet):
    queryset = DailyWorkDescription.objects.select_related(
        'derrick_erection_operation'
    ).prefetch_related('transport_items__transport_type').all()
    serializer_class = DailyWorkDescriptionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DailyWorkDescriptionFilter
    search_fields = ['description']
    ordering_fields = ['id', 'created_at']
    ordering = ['-created_at']


@extend_schema_view(
    list=extend_schema(
        tags=["Kunlik transport vositalari"],
        summary="Jalb qilingan transportlar ro'yxati",
        description="Kunlik hisobotlarga biriktirilgan transport vositalari ro'yxati va ularning soni."
    ),
    create=extend_schema(
        tags=["Kunlik transport vositalari"],
        summary="Kunlik hisobotga transport biriktirish",
        description="Kunlik ish hisobotiga muayyan transport turi va sonini qo'shish."
    ),
    retrieve=extend_schema(
        tags=["Kunlik transport vositalari"],
        summary="Bitta transport ma'lumotlari",
        description="ID bo'yicha transport vositasi tafsilotlari."
    ),
    update=extend_schema(
        tags=["Kunlik transport vositalari"],
        summary="Transport ma'lumotlarini to'liq yangilash",
        description="Transport turi yoki sonini to'liq yangilash."
    ),
    partial_update=extend_schema(
        tags=["Kunlik transport vositalari"],
        summary="Transport ma'lumotlarini qisman yangilash",
        description="Transport soni yoki tavsifini qisman yangilash."
    ),
    destroy=extend_schema(
        tags=["Kunlik transport vositalari"],
        summary="Transport yozuvini o'chirish",
        description="Transport yozuvini tizimdan o'chirish."
    ),
)
class DailyTransportItemViewSet(viewsets.ModelViewSet):
    queryset = DailyTransportItem.objects.select_related('daily_work_description', 'transport_type').all()
    serializer_class = DailyTransportItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DailyTransportItemFilter
    search_fields = ['description', 'transport_type__name']
    ordering_fields = ['id', 'count', 'created_at']
    ordering = ['-id']
