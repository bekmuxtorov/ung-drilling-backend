from rest_framework import serializers
from apps.directory.serializers import (
    EnterpriseSerializer,
    DrillingRigTypeSerializer,
    AreaSerializer,
    ForemanSerializer,
    TransportTypeSerializer,
)
from apps.directory.models import (
    Enterprise,
    DrillingRigType,
    Area,
    Foreman,
    TransportType,
)
from .models import (
    DerrickErectionOperation,
    OperationStage,
    DailyWorkDescription,
    DailyTransportItem,
)


class OperationStageSerializer(serializers.ModelSerializer):
    """
    Operatsiya bosqichi serializatori (Demontaj, Tashish, Montaj).
    """
    stage_type_display = serializers.CharField(source='get_stage_type_display', read_only=True)

    class Meta:
        model = OperationStage
        fields = [
            'id',
            'operation',
            'stage_type',
            'stage_type_display',
            'plan_days',
            'fact_days',
            'plan_start_date',
            'plan_end_date',
            'fact_start_date',
            'fact_end_date',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        # Sanalarni tekshirish (start <= end)
        plan_start = attrs.get('plan_start_date', getattr(self.instance, 'plan_start_date', None))
        plan_end = attrs.get('plan_end_date', getattr(self.instance, 'plan_end_date', None))
        if plan_start and plan_end and plan_end < plan_start:
            raise serializers.ValidationError({
                "plan_end_date": "Rejadagi tugash sanasi boshlanish sanasidan oldin bo'lishi mumkin emas."
            })

        fact_start = attrs.get('fact_start_date', getattr(self.instance, 'fact_start_date', None))
        fact_end = attrs.get('fact_end_date', getattr(self.instance, 'fact_end_date', None))
        if fact_start and fact_end and fact_end < fact_start:
            raise serializers.ValidationError({
                "fact_end_date": "Amaldagi tugash sanasi boshlanish sanasidan oldin bo'lishi mumkin emas."
            })

        return attrs


class DailyTransportItemSerializer(serializers.ModelSerializer):
    """
    Kunlik ish hisobotiga biriktirilgan transport vositasi serializatori.
    """
    transport_type = serializers.PrimaryKeyRelatedField(
        queryset=TransportType.objects.all(),
        write_only=True
    )

    class Meta:
        model = DailyTransportItem
        fields = [
            'id',
            'daily_work_description',
            'transport_type',
            'count',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['transport_type'] = TransportTypeSerializer(instance.transport_type).data
        return representation


class DailyWorkDescriptionSerializer(serializers.ModelSerializer):
    """
    Kunlik ish tavsifi (hisoboti) serializatori.
    Transport vositalari ro'yxatini ichma-ich (nested) ko'rinishda taqdim etadi.
    """
    transport_items = DailyTransportItemSerializer(many=True, read_only=True)

    class Meta:
        model = DailyWorkDescription
        fields = [
            'id',
            'derrick_erection_operation',
            'description',
            'transport_items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DerrickErectionOperationSerializer(serializers.ModelSerializer):
    """
    VBM Operatsiyasi serializatori.
    Read amallarida bog'langan obyektlar (enterprise, rig, areas, foreman) to'liq ob'yekt sifatida qaytariladi.
    Write amallarida esa ularning ID raqamlari qabul qilinadi.
    """
    enterprise = serializers.PrimaryKeyRelatedField(
        queryset=Enterprise.objects.all(),
        write_only=True
    )
    drilling_rig_type = serializers.PrimaryKeyRelatedField(
        queryset=DrillingRigType.objects.all(),
        write_only=True
    )
    from_area = serializers.PrimaryKeyRelatedField(
        queryset=Area.objects.all(),
        write_only=True
    )
    to_area = serializers.PrimaryKeyRelatedField(
        queryset=Area.objects.all(),
        write_only=True
    )
    foreman = serializers.PrimaryKeyRelatedField(
        queryset=Foreman.objects.all(),
        write_only=True
    )
    stages = OperationStageSerializer(many=True, read_only=True)
    daily_works_count = serializers.IntegerField(source='daily_works.count', read_only=True)

    class Meta:
        model = DerrickErectionOperation
        fields = [
            'id',
            'enterprise',
            'drilling_rig_type',
            'from_area',
            'from_well_number',
            'to_area',
            'to_well_number',
            'foreman',
            'number_employees',
            'distance_km',
            'plan_days',
            'expected_drilling_date',
            'completion_percentage',
            'delay_reason',
            'work_description',
            'stages',
            'daily_works_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_completion_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Bajarilish foizi 0.00 va 100.00 oralig'ida bo'lishi kerak.")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['enterprise'] = EnterpriseSerializer(instance.enterprise).data
        representation['drilling_rig_type'] = DrillingRigTypeSerializer(instance.drilling_rig_type).data
        representation['from_area'] = AreaSerializer(instance.from_area).data
        representation['to_area'] = AreaSerializer(instance.to_area).data
        representation['foreman'] = ForemanSerializer(instance.foreman).data
        return representation
