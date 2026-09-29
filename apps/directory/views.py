from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import (
    Enterprise,
    DrillingRigType,
    Region,
    Area,
    Foreman,
    TransportType,
    Position,
    Employee,
    OperationStageType,
)
from .serializers import (
    EnterpriseSerializer,
    DrillingRigTypeSerializer,
    RegionSerializer,
    AreaSerializer,
    ForemanSerializer,
    TransportTypeSerializer,
    PositionSerializer,
    EmployeeSerializer,
    OperationStageChoiceSerializer,
)
from .filters import (
    EnterpriseFilter,
    DrillingRigTypeFilter,
    RegionFilter,
    AreaFilter,
    ForemanFilter,
    TransportTypeFilter,
    PositionFilter,
    EmployeeFilter,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Korxonalar"],
        summary="Barcha korxonalar ro'yxati",
        description="Mavjud korxonalar ro'yxatini qaytaradi. Nom bo'yicha qidirish va saralash imkoniyati mavjud."
    ),
    create=extend_schema(
        tags=["Korxonalar"],
        summary="Yangi korxona qo'shish",
        description="Tizimga yangi korxona ma'lumotlarini kiritish."
    ),
    retrieve=extend_schema(
        tags=["Korxonalar"],
        summary="Bitta korxona ma'lumotlarini olish",
        description="ID bo'yicha korxonaning batafsil ma'lumotlarini olish."
    ),
    update=extend_schema(
        tags=["Korxonalar"],
        summary="Korxona ma'lumotlarini to'liq yangilash",
        description="Mavjud korxona ma'lumotlarini to'liq tahrirlash (PUT)."
    ),
    partial_update=extend_schema(
        tags=["Korxonalar"],
        summary="Korxona ma'lumotlarini qisman yangilash",
        description="Korxona ma'lumotlarining tanlangan maydonlarini tahrirlash (PATCH)."
    ),
    destroy=extend_schema(
        tags=["Korxonalar"],
        summary="Korxonani o'chirish",
        description="Berilgan ID ga tegishli korxonani tizimdan o'chirish."
    ),
)
class EnterpriseViewSet(viewsets.ModelViewSet):
    queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EnterpriseFilter
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['-id']


@extend_schema_view(
    list=extend_schema(
        tags=["Burg'ulash uskunalari"],
        summary="Burg'ulash uskunasi turlari ro'yxati",
        description="Barcha burg'ulash qurilmalari turlarini paginatsiya bilan qaytaradi."
    ),
    create=extend_schema(
        tags=["Burg'ulash uskunalari"],
        summary="Yangi uskuna turi qo'shish",
        description="Tizimga yangi burg'ulash uskunasi turini qo'shish."
    ),
    retrieve=extend_schema(
        tags=["Burg'ulash uskunalari"],
        summary="Bitta uskuna turi ma'lumotlari",
        description="ID bo'yicha uskuna turining batafsil ma'lumotlari."
    ),
    update=extend_schema(
        tags=["Burg'ulash uskunalari"],
        summary="Uskuna turini to'liq yangilash",
        description="Mavjud uskuna turini to'liq yangilash (PUT)."
    ),
    partial_update=extend_schema(
        tags=["Burg'ulash uskunalari"],
        summary="Uskuna turini qisman yangilash",
        description="Mavjud uskuna turining qisman maydonlarini yangilash (PATCH)."
    ),
    destroy=extend_schema(
        tags=["Burg'ulash uskunalari"],
        summary="Uskuna turini o'chirish",
        description="Berilgan uskuna turini tizimdan o'chirish."
    ),
)
class DrillingRigTypeViewSet(viewsets.ModelViewSet):
    queryset = DrillingRigType.objects.all()
    serializer_class = DrillingRigTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DrillingRigTypeFilter
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['-id']


@extend_schema_view(
    list=extend_schema(
        tags=["Hududlar (Viloyatlar)"],
        summary="Hududlar (Viloyatlar) ro'yxati",
        description="O'zbekiston viloyatlari va hududlari ro'yxatini qaytaradi."
    ),
    create=extend_schema(
        tags=["Hududlar (Viloyatlar)"],
        summary="Yangi hudud qo'shish",
        description="Tizimga yangi viloyat / hudud kiritish."
    ),
    retrieve=extend_schema(
        tags=["Hududlar (Viloyatlar)"],
        summary="Bitta hudud ma'lumotlari",
        description="ID bo'yicha hudud ma'lumotlari."
    ),
    update=extend_schema(
        tags=["Hududlar (Viloyatlar)"],
        summary="Hududni to'liq yangilash",
        description="Mavjud hudud nomini to'liq yangilash."
    ),
    partial_update=extend_schema(
        tags=["Hududlar (Viloyatlar)"],
        summary="Hududni qisman yangilash",
        description="Hudud ma'lumotlarini qisman yangilash."
    ),
    destroy=extend_schema(
        tags=["Hududlar (Viloyatlar)"],
        summary="Hududni o'chirish",
        description="Hududni tizimdan o'chirish."
    ),
)
class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RegionFilter
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['-id']


@extend_schema_view(
    list=extend_schema(
        tags=["Maydonlar (Konlar)"],
        summary="Maydonlar (Konlar) ro'yxati",
        description=(
            "Neft va gaz konlari (maydonlari) ro'yxati. "
            "`?region_id=ID` parametri orqali aniq viloyatga tegishli maydonlarni filtrlash mumkin. "
            "`region` ma'lumoti to'liq nested obyekt sifatida qaytadi."
        )
    ),
    create=extend_schema(
        tags=["Maydonlar (Konlar)"],
        summary="Yangi maydon qo'shish",
        description="Yangi maydon qo'shish. `region` maydoniga hududning butun son ID qiymati uzatiladi."
    ),
    retrieve=extend_schema(
        tags=["Maydonlar (Konlar)"],
        summary="Bitta maydon ma'lumotlari",
        description="ID bo'yicha maydon ma'lumotlari va unga biriktirilgan viloyat."
    ),
    update=extend_schema(
        tags=["Maydonlar (Konlar)"],
        summary="Maydonni to'liq yangilash",
        description="Maydon nomini va tegishli viloyatini to'liq yangilash (PUT)."
    ),
    partial_update=extend_schema(
        tags=["Maydonlar (Konlar)"],
        summary="Maydonni qisman yangilash",
        description="Maydon ma'lumotlarini qisman yangilash (PATCH)."
    ),
    destroy=extend_schema(
        tags=["Maydonlar (Konlar)"],
        summary="Maydonni o'chirish",
        description="Maydonni tizimdan o'chirish."
    ),
)
class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.select_related('region').all()
    serializer_class = AreaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AreaFilter
    search_fields = ['name', 'region__name']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['-id']


@extend_schema_view(
    list=extend_schema(
        tags=["Ustalar (Foremen)"],
        summary="Ustalar (Prorablar) ro'yxati",
        description="Burg'ulash ustalari va prorablar ro'yxati. Ism va telefon raqami bo'yicha qidiruv mavjud."
    ),
    create=extend_schema(
        tags=["Ustalar (Foremen)"],
        summary="Yangi usta qo'shish",
        description="Yangi usta (prorab) va uning telefon raqamini kiritish."
    ),
    retrieve=extend_schema(
        tags=["Ustalar (Foremen)"],
        summary="Bitta usta ma'lumotlari",
        description="ID bo'yicha usta ma'lumotlari."
    ),
    update=extend_schema(
        tags=["Ustalar (Foremen)"],
        summary="Usta ma'lumotlarini to'liq yangilash",
        description="Usta ma'lumotlarini to'liq yangilash."
    ),
    partial_update=extend_schema(
        tags=["Ustalar (Foremen)"],
        summary="Usta ma'lumotlarini qisman yangilash",
        description="Usta ma'lumotlarini qisman yangilash."
    ),
    destroy=extend_schema(
        tags=["Ustalar (Foremen)"],
        summary="Ustani o'chirish",
        description="Ustani tizimdan o'chirish."
    ),
)
class ForemanViewSet(viewsets.ModelViewSet):
    queryset = Foreman.objects.all()
    serializer_class = ForemanSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ForemanFilter
    search_fields = ['name', 'phone']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['-id']


@extend_schema_view(
    list=extend_schema(
        tags=["Transport turlari"],
        summary="Transport turlari ro'yxati",
        description="Tashish va logistika jarayonlarida qatnashuvchi barcha transport vositalari turlari."
    ),
    create=extend_schema(
        tags=["Transport turlari"],
        summary="Yangi transport turi qo'shish",
        description="Yangi transport turi kiritish."
    ),
    retrieve=extend_schema(
        tags=["Transport turlari"],
        summary="Bitta transport turi ma'lumotlari",
        description="ID bo'yicha transport turi ma'lumotlari."
    ),
    update=extend_schema(
        tags=["Transport turlari"],
        summary="Transport turini to'liq yangilash",
        description="Transport turini to'liq yangilash."
    ),
    partial_update=extend_schema(
        tags=["Transport turlari"],
        summary="Transport turini qisman yangilash",
        description="Transport turini qisman yangilash."
    ),
    destroy=extend_schema(
        tags=["Transport turlari"],
        summary="Transport turini o'chirish",
        description="Transport turini tizimdan o'chirish."
    ),
)
class TransportTypeViewSet(viewsets.ModelViewSet):
    queryset = TransportType.objects.all()
    serializer_class = TransportTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransportTypeFilter
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['-id']


@extend_schema_view(
    list=extend_schema(
        tags=["Lavozimlar"],
        summary="Lavozimlar ro'yxati",
        description="Korxonadagi barcha xizmat lavozimlari ro'yxati."
    ),
    create=extend_schema(
        tags=["Lavozimlar"],
        summary="Yangi lavozim qo'shish",
        description="Yangi lavozim yaratish."
    ),
    retrieve=extend_schema(
        tags=["Lavozimlar"],
        summary="Bitta lavozim ma'lumotlari",
        description="ID bo'yicha lavozim ma'lumotlari."
    ),
    update=extend_schema(
        tags=["Lavozimlar"],
        summary="Lavozimni to'liq yangilash",
        description="Lavozim nomini to'liq yangilash."
    ),
    partial_update=extend_schema(
        tags=["Lavozimlar"],
        summary="Lavozimni qisman yangilash",
        description="Lavozim nomini qisman yangilash."
    ),
    destroy=extend_schema(
        tags=["Lavozimlar"],
        summary="Lavozimni o'chirish",
        description="Lavozimni tizimdan o'chirish."
    ),
)
class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PositionFilter
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['-id']


@extend_schema_view(
    list=extend_schema(
        tags=["Xodimlar"],
        summary="Xodimlar ro'yxati",
        description=(
            "Korxona xodimlari ro'yxati. "
            "`?position_id=ID` parametri orqali muayyan lavozimdagi xodimlarni filtrlash mumkin. "
            "`position` maydoni to'liq obyekt sifatida qaytadi."
        )
    ),
    create=extend_schema(
        tags=["Xodimlar"],
        summary="Yangi xodim qo'shish",
        description="Yangi xodim kiritish. `position` maydoniga tegishli lavozim ID si yuboriladi."
    ),
    retrieve=extend_schema(
        tags=["Xodimlar"],
        summary="Bitta xodim ma'lumotlari",
        description="ID bo'yicha xodimning batafsil ma'lumotlari va lavozimi."
    ),
    update=extend_schema(
        tags=["Xodimlar"],
        summary="Xodim ma'lumotlarini to'liq yangilash",
        description="Xodim ma'lumotlarini to'liq yangilash (PUT)."
    ),
    partial_update=extend_schema(
        tags=["Xodimlar"],
        summary="Xodim ma'lumotlarini qisman yangilash",
        description="Xodim ma'lumotlarini qisman yangilash (PATCH)."
    ),
    destroy=extend_schema(
        tags=["Xodimlar"],
        summary="Xodimni o'chirish",
        description="Xodimni tizimdan o'chirish."
    ),
)
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('position').all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = ['name', 'phone_number', 'position__name']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['-id']


class OperationStageTypeView(APIView):
    """
    Operatsiya bosqichlari (demontaj, tashish, montaj) ro'yxatini qaytaruvchi API.
    Frontend uchun qulay formatda taqdim etiladi.
    """
    @extend_schema(
        tags=["Operatsiya bosqichlari"],
        summary="Operatsiya bosqichlari (Enum) ro'yxati",
        description="Demontaj, Tashish va Montaj bosqichlari ro'yxatini qaytaradi (Frontend dropdownlari uchun).",
        responses={200: OperationStageChoiceSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        stages = [
            {"value": choice.value, "label": choice.label}
            for choice in OperationStageType
        ]
        return Response(stages, status=status.HTTP_200_OK)
