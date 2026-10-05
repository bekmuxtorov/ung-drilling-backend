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
    DrillingBPA,
    WellDesign,
    WellDesignInLength,
    DepthsLayersLength,
    DailyWorkDescriptionBPA,
    AvailableResourcesBPA,
)
from .serializers import (
    DerrickErectionOperationSerializer,
    OperationStageSerializer,
    DailyWorkDescriptionSerializer,
    DailyTransportItemSerializer,
    DrillingBPASerializer,
    DrillingBPADetailSerializer,
    WellDesignSerializer,
    WellDesignInLengthSerializer,
    DepthsLayersLengthSerializer,
    DailyWorkDescriptionBPASerializer,
    AvailableResourcesBPASerializer,
)
from .filters import (
    DerrickErectionOperationFilter,
    OperationStageFilter,
    DailyWorkDescriptionFilter,
    DailyTransportItemFilter,
    DrillingBPAFilter,
    WellDesignFilter,
    WellDesignInLengthFilter,
    DepthsLayersLengthFilter,
    DailyWorkDescriptionBPAFilter,
    AvailableResourcesBPAFilter,
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


@extend_schema_view(
    list=extend_schema(
        tags=["Burg'ulash (BPA) operatsiyalari"],
        summary="Barcha burg'ulash (BPA) operatsiyalari ro'yxati",
        description=(
            "Burg'ulash BPA operatsiyalari ro'yxatini qaytaradi. "
            "Filtrlash (korxona, maydon, quduq raqami, xodim, mashina turi, sanalar va chuqurlik), "
            "qidiruv va saralash imkoniyati mavjud. "
            "Erishilgan joriy chuqurlik (`current_depth` / `current_dept`) avtomatik hisoblab beriladi."
        )
    ),
    create=extend_schema(
        tags=["Burg'ulash (BPA) operatsiyalari"],
        summary="Yangi burg'ulash (BPA) operatsiyasini yaratish",
        description="Tizimga yangi BPA operatsiyasini kiritish."
    ),
    retrieve=extend_schema(
        tags=["Burg'ulash (BPA) operatsiyalari"],
        summary="Bitta BPA operatsiyasining to'liq ma'lumotlari",
        description=(
            "ID bo'yicha BPA operatsiyasining batafsil ma'lumotlari. "
            "Barcha ichki bo'limlar: quduq konstruksiyasi, o'tish dinamikasi (plan/fact), "
            "qatlamlar chuqurliklari, kunlik eritmalar va ish hisobotlari hamda mavjud resurslar ro'yxati bilan birga qaytadi."
        ),
        responses={200: DrillingBPADetailSerializer}
    ),
    update=extend_schema(
        tags=["Burg'ulash (BPA) operatsiyalari"],
        summary="BPA operatsiyasini to'liq yangilash",
        description="Mavjud BPA operatsiyasini to'liq yangilash (PUT)."
    ),
    partial_update=extend_schema(
        tags=["Burg'ulash (BPA) operatsiyalari"],
        summary="BPA operatsiyasini qisman yangilash",
        description="BPA operatsiyasining ayrim parametrlarini qisman yangilash (PATCH)."
    ),
    destroy=extend_schema(
        tags=["Burg'ulash (BPA) operatsiyalari"],
        summary="BPA operatsiyasini o'chirish",
        description="Berilgan ID ga tegishli BPA operatsiyasini tizimdan o'chirish."
    ),
)
class DrillingBPAViewSet(viewsets.ModelViewSet):
    queryset = (
        DrillingBPA.objects
        .select_related('enterprise', 'employee', 'employee__position', 'area', 'area__region', 'machine_type')
        .prefetch_related(
            'well_designs',
            'well_designs_in_length',
            'depths_layers_lengths',
            'daily_works',
            'available_resources',
        )
        .all()
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DrillingBPAFilter
    search_fields = ['number', 'well_number', 'area__name', 'enterprise__name', 'employee__name']
    ordering_fields = ['id', 'number', 'well_number', 'drilling_start_date', 'depth_plan', 'created_at']
    ordering = ['-id']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DrillingBPADetailSerializer
        return DrillingBPASerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Quduq konstruksiyasi (Well Design)"],
        summary="Quduq konstruksiyalari ro'yxati",
        description="Barcha quduq konstruksiyalari (quvur diametri, uzunligi, reja/fakt). `?drilling_bpa=ID` orqali filtrlash mumkin."
    ),
    create=extend_schema(
        tags=["Quduq konstruksiyasi (Well Design)"],
        summary="Yangi quduq konstruksiyasini qo'shish",
        description="Muayyan BPA operatsiyasiga yangi quduq konstruksiyasi parametrlarini biriktirish."
    ),
    retrieve=extend_schema(
        tags=["Quduq konstruksiyasi (Well Design)"],
        summary="Bitta quduq konstruksiyasi ma'lumotlari",
        description="ID bo'yicha quduq konstruksiyasi tafsilotlari."
    ),
    update=extend_schema(
        tags=["Quduq konstruksiyasi (Well Design)"],
        summary="Quduq konstruksiyasini to'liq yangilash",
        description="Quduq konstruksiyasini to'liq tahrirlash (PUT)."
    ),
    partial_update=extend_schema(
        tags=["Quduq konstruksiyasi (Well Design)"],
        summary="Quduq konstruksiyasini qisman yangilash",
        description="Quduq konstruksiyasini qisman tahrirlash (PATCH)."
    ),
    destroy=extend_schema(
        tags=["Quduq konstruksiyasi (Well Design)"],
        summary="Quduq konstruksiyasini o'chirish",
        description="Quduq konstruksiyasi yozuvini tizimdan o'chirish."
    ),
)
class WellDesignViewSet(viewsets.ModelViewSet):
    queryset = WellDesign.objects.select_related('drilling_bpa').all()
    serializer_class = WellDesignSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = WellDesignFilter
    search_fields = ['drilling_bpa__well_number', 'drilling_bpa__number']
    ordering_fields = ['id', 'pipe_diameter', 'length', 'start_date', 'created_at']
    ordering = ['id']


@extend_schema_view(
    list=extend_schema(
        tags=["Quduq o'tish dinamikasi (Well Design in Length)"],
        summary="Quduq o'tish dinamikasi ro'yxati",
        description="Kunlik, oylik va yillik reja hamda faktik o'tish ko'rsatkichlari. Delta va delta_percent avtomatik hisoblanadi."
    ),
    create=extend_schema(
        tags=["Quduq o'tish dinamikasi (Well Design in Length)"],
        summary="Yangi o'tish ko'rsatkichini qo'shish",
        description="BPA bo'yicha kunlik, oylik yoki yillik reja/fakt uzunliklarini kiritish."
    ),
    retrieve=extend_schema(
        tags=["Quduq o'tish dinamikasi (Well Design in Length)"],
        summary="Bitta o'tish ko'rsatkichi ma'lumotlari",
        description="ID bo'yicha o'tish ko'rsatkichi, farq (delta) va foiz (delta_percent)."
    ),
    update=extend_schema(
        tags=["Quduq o'tish dinamikasi (Well Design in Length)"],
        summary="O'tish ko'rsatkichini to'liq yangilash",
        description="O'tish ko'rsatkichini to'liq tahrirlash (PUT)."
    ),
    partial_update=extend_schema(
        tags=["Quduq o'tish dinamikasi (Well Design in Length)"],
        summary="O'tish ko'rsatkichini qisman yangilash",
        description="O'tish ko'rsatkichini qisman tahrirlash (PATCH)."
    ),
    destroy=extend_schema(
        tags=["Quduq o'tish dinamikasi (Well Design in Length)"],
        summary="O'tish ko'rsatkichini o'chirish",
        description="O'tish ko'rsatkichini tizimdan o'chirish."
    ),
)
class WellDesignInLengthViewSet(viewsets.ModelViewSet):
    queryset = WellDesignInLength.objects.select_related('drilling_bpa').all()
    serializer_class = WellDesignInLengthSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = WellDesignInLengthFilter
    search_fields = ['drilling_bpa__well_number', 'drilling_bpa__number']
    ordering_fields = ['id', 'length_plan', 'length_fact', 'start_date', 'created_at']
    ordering = ['-start_date', '-id']


@extend_schema_view(
    list=extend_schema(
        tags=["Chuqurlik qatlamlari oraliqlari (Depths Layers Length)"],
        summary="Qatlamlar oraliqlari ro'yxati",
        description="BPA qudug'idagi geologik qatlamlar va ularning qalinligi/uzunligi ro'yxati."
    ),
    create=extend_schema(
        tags=["Chuqurlik qatlamlari oraliqlari (Depths Layers Length)"],
        summary="Yangi qatlam oralig'i qo'shish",
        description="BPA qudug'iga qatlam va uning uzunligini biriktirish."
    ),
    retrieve=extend_schema(
        tags=["Chuqurlik qatlamlari oraliqlari (Depths Layers Length)"],
        summary="Bitta qatlam oralig'i ma'lumotlari",
        description="ID bo'yicha qatlam va uzunligi tafsilotlari."
    ),
    update=extend_schema(
        tags=["Chuqurlik qatlamlari oraliqlari (Depths Layers Length)"],
        summary="Qatlam oralig'ini to'liq yangilash",
        description="Qatlam oralig'ini to'liq tahrirlash (PUT)."
    ),
    partial_update=extend_schema(
        tags=["Chuqurlik qatlamlari oraliqlari (Depths Layers Length)"],
        summary="Qatlam oralig'ini qisman yangilash",
        description="Qatlam oralig'ini qisman tahrirlash (PATCH)."
    ),
    destroy=extend_schema(
        tags=["Chuqurlik qatlamlari oraliqlari (Depths Layers Length)"],
        summary="Qatlam oralig'ini o'chirish",
        description="Qatlam oralig'ini tizimdan o'chirish."
    ),
)
class DepthsLayersLengthViewSet(viewsets.ModelViewSet):
    queryset = DepthsLayersLength.objects.select_related('drilling_bpa', 'layer').all()
    serializer_class = DepthsLayersLengthSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DepthsLayersLengthFilter
    search_fields = ['drilling_bpa__well_number', 'layer__name']
    ordering_fields = ['id', 'length', 'created_at']
    ordering = ['id']


@extend_schema_view(
    list=extend_schema(
        tags=["BPA kunlik ish hisobotlari (Daily Works BPA)"],
        summary="BPA kunlik ish va eritmalar hisobotlari",
        description="BPA bo'yicha kunlik bajarilgan ishlar va burg'ulash eritmasi/parametrlari (density, viscosity, flow_rate, rpm va h.k.)."
    ),
    create=extend_schema(
        tags=["BPA kunlik ish hisobotlari (Daily Works BPA)"],
        summary="Yangi BPA kunlik hisobotini kiritish",
        description="Kunlik hisobot sanasi, tavsifi va barcha eritma/bosim parametrlarini ro'yxatga olish."
    ),
    retrieve=extend_schema(
        tags=["BPA kunlik ish hisobotlari (Daily Works BPA)"],
        summary="Bitta BPA kunlik hisoboti ma'lumotlari",
        description="ID bo'yicha kunlik hisobotning barcha texnologik parametrlari."
    ),
    update=extend_schema(
        tags=["BPA kunlik ish hisobotlari (Daily Works BPA)"],
        summary="BPA kunlik hisobotini to'liq yangilash",
        description="Kunlik hisobotni to'liq tahrirlash (PUT)."
    ),
    partial_update=extend_schema(
        tags=["BPA kunlik ish hisobotlari (Daily Works BPA)"],
        summary="BPA kunlik hisobotini qisman yangilash",
        description="Kunlik hisobotni qisman tahrirlash (PATCH)."
    ),
    destroy=extend_schema(
        tags=["BPA kunlik ish hisobotlari (Daily Works BPA)"],
        summary="BPA kunlik hisobotini o'chirish",
        description="Kunlik hisobotni tizimdan o'chirish."
    ),
)
class DailyWorkDescriptionBPAViewSet(viewsets.ModelViewSet):
    queryset = DailyWorkDescriptionBPA.objects.select_related('drilling_bpa').all()
    serializer_class = DailyWorkDescriptionBPASerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DailyWorkDescriptionBPAFilter
    search_fields = ['drilling_bpa__well_number', 'description']
    ordering_fields = ['id', 'report_date', 'density', 'viscosity', 'created_at']
    ordering = ['-report_date', '-id']


@extend_schema_view(
    list=extend_schema(
        tags=["BPA mavjud resurslari (Available Resources BPA)"],
        summary="BPA mavjud resurslari ro'yxati",
        description="BPA qudug'iga ajratilgan moddiy resurslar, ularning o'lchov birligi va miqdori."
    ),
    create=extend_schema(
        tags=["BPA mavjud resurslari (Available Resources BPA)"],
        summary="BPA ga yangi resurs biriktirish",
        description="BPA bo'yicha resurs turi, o'lchov birligi va miqdorini kiritish."
    ),
    retrieve=extend_schema(
        tags=["BPA mavjud resurslari (Available Resources BPA)"],
        summary="Bitta mavjud resurs ma'lumotlari",
        description="ID bo'yicha resurs, o'lchov birligi va miqdori tafsilotlari."
    ),
    update=extend_schema(
        tags=["BPA mavjud resurslari (Available Resources BPA)"],
        summary="Mavjud resursni to'liq yangilash",
        description="Mavjud resurs ma'lumotlarini to'liq tahrirlash (PUT)."
    ),
    partial_update=extend_schema(
        tags=["BPA mavjud resurslari (Available Resources BPA)"],
        summary="Mavjud resursni qisman yangilash",
        description="Mavjud resurs miqdori yoki tavsifini qisman tahrirlash (PATCH)."
    ),
    destroy=extend_schema(
        tags=["BPA mavjud resurslari (Available Resources BPA)"],
        summary="Mavjud resursni o'chirish",
        description="Mavjud resurs yozuvini tizimdan o'chirish."
    ),
)
class AvailableResourcesBPAViewSet(viewsets.ModelViewSet):
    queryset = AvailableResourcesBPA.objects.select_related('drilling_bpa', 'resources', 'unit').all()
    serializer_class = AvailableResourcesBPASerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AvailableResourcesBPAFilter
    search_fields = ['drilling_bpa__well_number', 'resources__name', 'description']
    ordering_fields = ['id', 'value', 'created_at']
    ordering = ['-id']

