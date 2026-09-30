from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema_field
from apps.directory.models import Employee
from .models import Role

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    """
    Django Permission ma'lumotlari uchun serializer.
    """
    app_label = serializers.CharField(source='content_type.app_label', read_only=True)
    model = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'app_label', 'model']


class RoleSerializer(serializers.ModelSerializer):
    """
    Role ma'lumotnomasi uchun serializer.
    """
    permissions_detail = PermissionSerializer(source='permissions', many=True, read_only=True)
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False,
        write_only=False
    )

    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'permissions',
            'permissions_detail',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoleShortSerializer(serializers.ModelSerializer):
    """
    Qisqartirilgan Role serializeri (User ma'lumotlari ichida qaytarish uchun).
    """
    class Meta:
        model = Role
        fields = ['id', 'name']


class EmployeeShortSerializer(serializers.ModelSerializer):
    """
    Qisqartirilgan Xodim (Employee) serializeri.
    """
    position_name = serializers.CharField(source='position.name', read_only=True, default=None)

    class Meta:
        model = Employee
        fields = ['id', 'name', 'phone_number', 'position', 'position_name']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    JWT Token olish serializeri (Login).
    Token payload va response tarkibiga qo'shimcha foydalanuvchi ma'lumotlarini qo'shadi.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # JWT Payload ichiga custom claim'lar qo'shish
        token['username'] = user.username
        token['email'] = user.email
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff
        token['role_id'] = user.role_id
        token['role'] = user.role.name if user.role else None
        token['employee_id'] = user.employee_id
        token['employee_name'] = user.employee.name if user.employee else None

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        role_data = RoleShortSerializer(user.role).data if user.role else None
        employee_data = EmployeeShortSerializer(user.employee).data if user.employee else None

        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'role': role_data,
            'employee': employee_data,
            'permissions': user.get_all_permissions_list(),
            'created_at': user.created_at,
            'updated_at': user.updated_at,
        }

        return data


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Foydalanuvchi ma'lumotlarini to'liq ko'rish uchun serializer.
    """
    role_detail = RoleShortSerializer(source='role', read_only=True)
    employee_detail = EmployeeShortSerializer(source='employee', read_only=True)
    employee_name = serializers.CharField(source='employee.name', read_only=True, default=None)
    role_name = serializers.CharField(source='role.name', read_only=True, default=None)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'employee',
            'employee_name',
            'employee_detail',
            'role',
            'role_name',
            'role_detail',
            'permissions',
            'created_at',
            'updated_at',
            'last_login',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'last_login',
            'permissions',
            'employee_name',
            'employee_detail',
            'role_name',
            'role_detail',
        ]

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_permissions(self, obj):
        return obj.get_all_permissions_list()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Yangi foydalanuvchi yaratish uchun serializer.
    Parol xavfsiz heshlanadi.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'password_confirm',
            'email',
            'first_name',
            'last_name',
            'employee',
            'role',
            'is_active',
            'is_staff',
            'is_superuser',
        ]

    def validate(self, attrs):
        if attrs.get('password') != attrs.pop('password_confirm', None):
            raise serializers.ValidationError({"password_confirm": "Parollar bir-biriga mos kelmadi."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Foydalanuvchi ma'lumotlarini tahrirlash serializeri.
    """
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'employee',
            'role',
            'is_active',
            'is_staff',
            'is_superuser',
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Parolni o'zgartirish serializeri (Foydalanuvchining o'zi uchun).
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Yangi parollar mos kelmadi."})
        return attrs


class AdminSetPasswordSerializer(serializers.Serializer):
    """
    Admin tomonidan foydalanuvchi parolini yangilash serializeri.
    """
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Yangi parollar mos kelmadi."})
        return attrs
