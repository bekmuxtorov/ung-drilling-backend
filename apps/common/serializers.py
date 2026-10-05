from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import AuditLog


class AuditLogUserShortSerializer(serializers.Serializer):
    """Foydalanuvchi qisqa ma'lumotlari."""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Audit log (Audit Trail) serializatori.
    Qaysi foydalanuvchi, qaysi IP va MAC ID dan nima o'zgarish qilganini to'liq ko'rsatadi.
    """
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    user_detail = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'user_detail',
            'username',
            'user_full_name',
            'ip_address',
            'mac_address',
            'user_agent',
            'action',
            'action_display',
            'app_label',
            'model_name',
            'object_id',
            'object_repr',
            'changes',
            'old_values',
            'new_values',
            'created_at',
        ]
        read_only_fields = fields

    @extend_schema_field(AuditLogUserShortSerializer)
    def get_user_detail(self, obj):
        if not obj.user:
            return None
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': getattr(obj.user, 'get_full_name', lambda: '')() or obj.user_full_name or obj.user.username,
        }
