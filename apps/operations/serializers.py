from rest_framework import serializers
from apps.directory.serializers import (
    EnterpriseSerializer,
    DrillingRigTypeSerializer,
    AreaSerializer,
    ForemanSerializer,
    TransportTypeSerializer,
    EmployeeSerializer,
    MachineTypeSerializer,
    DepthsLayersSerializer,
    ResourcesSerializer,
    UnitSerializer,
)
from apps.directory.models import (
    Enterprise,
    DrillingRigType,
    Area,
    Foreman,
    TransportType,
    Employee,
    MachineType,
    DepthsLayers,
    Resources,
    Unit,
)
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
    WellDesignType,
    WellDesignPeriodType,
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


class WellDesignSerializer(serializers.ModelSerializer):
    """
    Quduq konstruksiyasi (Well Design) serializatori.
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = WellDesign
        fields = [
            'id',
            'drilling_bpa',
            'type',
            'type_display',
            'pipe_diameter',
            'length',
            'start_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WellDesignInLengthSerializer(serializers.ModelSerializer):
    """
    Quduq o'tish dinamikasi (Well Design In Length) serializatori.
    Delta va delta foiz avtomatik hisoblab beriladi.
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    delta = serializers.FloatField(read_only=True)
    delta_percent = serializers.FloatField(read_only=True)

    class Meta:
        model = WellDesignInLength
        fields = [
            'id',
            'drilling_bpa',
            'type',
            'type_display',
            'length_plan',
            'length_fact',
            'delta',
            'delta_percent',
            'start_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'delta', 'delta_percent', 'created_at', 'updated_at']


class DepthsLayersLengthSerializer(serializers.ModelSerializer):
    """
    Chuqurlik qatlamlari oraliqlari (Depths Layers Length) serializatori.
    """
    layer = serializers.PrimaryKeyRelatedField(
        queryset=DepthsLayers.objects.all(),
        write_only=True
    )

    class Meta:
        model = DepthsLayersLength
        fields = [
            'id',
            'drilling_bpa',
            'layer',
            'length',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.layer:
            representation['layer'] = DepthsLayersSerializer(instance.layer).data
        return representation


class DailyWorkDescriptionBPASerializer(serializers.ModelSerializer):
    """
    BPA bo'yicha kunlik ish hisoboti va burg'ulash eritmasi parametrlari serializatori.
    """
    density = serializers.FloatField(required=False, default=0.0, allow_null=True)
    viscosity = serializers.FloatField(required=False, default=0.0, allow_null=True)
    fluid_loss = serializers.FloatField(required=False, default=0.0, allow_null=True)
    mud_cake = serializers.FloatField(required=False, default=0.0, allow_null=True)
    ph_level = serializers.FloatField(required=False, default=0.0, allow_null=True)
    weight_on_bit = serializers.FloatField(required=False, default=0.0, allow_null=True)
    rpm = serializers.FloatField(required=False, default=0.0, allow_null=True)
    pump_pressure = serializers.FloatField(required=False, default=0.0, allow_null=True)
    flow_rate = serializers.FloatField(required=False, default=0.0, allow_null=True)

    class Meta:
        model = DailyWorkDescriptionBPA
        fields = [
            'id',
            'drilling_bpa',
            'report_date',
            'description',
            'density',
            'viscosity',
            'fluid_loss',
            'mud_cake',
            'ph_level',
            'weight_on_bit',
            'rpm',
            'pump_pressure',
            'flow_rate',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        for field in [
            'density', 'viscosity', 'fluid_loss', 'mud_cake',
            'ph_level', 'weight_on_bit', 'rpm', 'pump_pressure', 'flow_rate'
        ]:
            if attrs.get(field) is None:
                attrs[field] = 0.0
        return super().validate(attrs)


class AvailableResourcesBPASerializer(serializers.ModelSerializer):
    """
    BPA bo'yicha mavjud / ishlatilgan resurslar serializatori.
    """
    resources = serializers.PrimaryKeyRelatedField(
        queryset=Resources.objects.all(),
        write_only=True
    )
    unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        write_only=True
    )

    class Meta:
        model = AvailableResourcesBPA
        fields = [
            'id',
            'drilling_bpa',
            'resources',
            'unit',
            'value',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.resources:
            representation['resources'] = ResourcesSerializer(instance.resources).data
        if instance.unit:
            representation['unit'] = UnitSerializer(instance.unit).data
        return representation


class DrillingBPASerializer(serializers.ModelSerializer):
    """
    Burg'ulash (BPA) operatsiyasi asosiy ro'yxat serializatori.
    Foreign keylar o'qishda to'liq obyekt, yozishda ID sifatida boshqariladi.
    Hozirgi chuqurlik (current_depth / current_dept) hisoblab beriladi.
    """
    enterprise = serializers.PrimaryKeyRelatedField(
        queryset=Enterprise.objects.all(),
        write_only=True
    )
    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    area = serializers.PrimaryKeyRelatedField(
        queryset=Area.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    machine_type = serializers.PrimaryKeyRelatedField(
        queryset=MachineType.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    current_depth = serializers.FloatField(read_only=True)
    current_dept = serializers.FloatField(read_only=True)
    well_designs_count = serializers.IntegerField(source='well_designs.count', read_only=True)
    daily_works_count = serializers.IntegerField(source='daily_works.count', read_only=True)
    available_resources_count = serializers.IntegerField(source='available_resources.count', read_only=True)

    class Meta:
        model = DrillingBPA
        fields = [
            'id',
            'number',
            'enterprise',
            'employee',
            'area',
            'well_number',
            'machine_type',
            'drilling_start_date',
            'depth_plan',
            'current_depth',
            'current_dept',
            'well_designs_count',
            'daily_works_count',
            'available_resources_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'current_depth', 'current_dept', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['enterprise'] = EnterpriseSerializer(instance.enterprise).data if instance.enterprise else None
        representation['employee'] = EmployeeSerializer(instance.employee).data if instance.employee else None
        representation['area'] = AreaSerializer(instance.area).data if instance.area else None
        representation['machine_type'] = MachineTypeSerializer(instance.machine_type).data if instance.machine_type else None
        return representation


class DrillingBPADetailSerializer(DrillingBPASerializer):
    """
    Bitta BPA operatsiyasining batafsil ko'rinishi (barcha ichki bo'limlar bilan birga).
    """
    well_designs = WellDesignSerializer(many=True, read_only=True)
    well_designs_in_length = WellDesignInLengthSerializer(many=True, read_only=True)
    depths_layers_lengths = DepthsLayersLengthSerializer(many=True, read_only=True)
    daily_works = DailyWorkDescriptionBPASerializer(many=True, read_only=True)
    available_resources = AvailableResourcesBPASerializer(many=True, read_only=True)

    class Meta(DrillingBPASerializer.Meta):
        fields = DrillingBPASerializer.Meta.fields + [
            'well_designs',
            'well_designs_in_length',
            'depths_layers_lengths',
            'daily_works',
            'available_resources',
        ]

