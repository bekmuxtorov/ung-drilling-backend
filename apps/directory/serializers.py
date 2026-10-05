from rest_framework import serializers
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
    MachineType,
    DepthsLayers,
    Resources,
    Unit,
)


class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DrillingRigTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrillingRigType
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AreaSerializer(serializers.ModelSerializer):
    """
    Maydon (Area) serializatori.
    Read amallarida bog'langan hudud (region) ma'lumotlarini to'liq obyekt sifatida,
    Write amallarida esa region ID (Primary Key) sifatida qabul qiladi.
    """
    region = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        write_only=True
    )

    class Meta:
        model = Area
        fields = ['id', 'name', 'region', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['region'] = RegionSerializer(instance.region).data
        return representation


class ForemanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foreman
        fields = ['id', 'name', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransportTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportType
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Xodim (Employee) serializatori.
    Read amallarida lavozim (position) obyektini to'liq ko'rsatadi,
    Write amallarida esa position ID sifatida qabul qiladi.
    """
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        write_only=True
    )

    class Meta:
        model = Employee
        fields = ['id', 'name', 'phone_number', 'position', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['position'] = PositionSerializer(instance.position).data
        return representation


class OperationStageChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class MachineTypeSerializer(serializers.ModelSerializer):
    """
    Mashina turi (Machine Type) serializatori.
    """
    class Meta:
        model = MachineType
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepthsLayersSerializer(serializers.ModelSerializer):
    """
    Chuqurlik qatlami (Depths Layer) serializatori.
    """
    class Meta:
        model = DepthsLayers
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


DepthLayerSerializer = DepthsLayersSerializer


class ResourcesSerializer(serializers.ModelSerializer):
    """
    Resurs (Resources) serializatori.
    """
    class Meta:
        model = Resources
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


ResourceSerializer = ResourcesSerializer


class UnitSerializer(serializers.ModelSerializer):
    """
    O'lchov birligi (Unit of Measurement) serializatori.
    """
    class Meta:
        model = Unit
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

