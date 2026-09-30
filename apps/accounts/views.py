from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Role
from .serializers import (
    CustomTokenObtainPairSerializer,
    RoleSerializer,
    PermissionSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    AdminSetPasswordSerializer,
)

User = get_user_model()


# ==============================================================================
# JWT Autentifikatsiya View'lari
# ==============================================================================

@extend_schema(
    tags=['Autentifikatsiya (JWT)'],
    summary="Tizimga kirish va JWT tokenlar olish (Login)",
    description="Username va password yuboriladi. Muvaffaqiyatli bo'lsa `access`, `refresh` tokenlar va `user` ma'lumotlari qaytadi."
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    tags=['Autentifikatsiya (JWT)'],
    summary="Access tokenni yangilash (Refresh)",
    description="Yaroqli `refresh` token yuborilib, yangi `access` token olinadi."
)
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(
    tags=['Autentifikatsiya (JWT)'],
    summary="Tokenni tekshirish (Verify)",
    description="Tokenning yaroqliligini (valid ekanligini) tekshiradi."
)
class CustomTokenVerifyView(TokenVerifyView):
    pass


@extend_schema(
    tags=['Autentifikatsiya (JWT)'],
    summary="Joriy tizimga kirgan foydalanuvchi ma'lumotlari (Me)",
    description="Token egasining shaxsiy ma'lumotlari, roli, xodim ma'lumotlari va ruxsatlarini olish hamda tahrirlash."
)
class CurrentUserView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserDetailSerializer


@extend_schema(
    tags=['Autentifikatsiya (JWT)'],
    summary="Parolni o'zgartirish",
    description="Joriy foydalanuvchi o'zining parolini eski parolni kiritish orqali yangilaydi.",
    request=ChangePasswordSerializer,
)
class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {"old_password": ["Amaldagi parol noto'g'ri kiritildi."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(
            {"detail": "Parol muvaffaqiyatli yangilandi."},
            status=status.HTTP_200_OK
        )


# ==============================================================================
# Rollar va Ruxsatlar View'lari
# ==============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Rollar va Ruxsatlar'], summary="Rollar ro'yxati"),
    create=extend_schema(tags=['Rollar va Ruxsatlar'], summary="Yangi rol yaratish"),
    retrieve=extend_schema(tags=['Rollar va Ruxsatlar'], summary="Rol tafsilotlari"),
    update=extend_schema(tags=['Rollar va Ruxsatlar'], summary="Rolni to'liq yangilash"),
    partial_update=extend_schema(tags=['Rollar va Ruxsatlar'], summary="Rolni qisman yangilash"),
    destroy=extend_schema(tags=['Rollar va Ruxsatlar'], summary="Rolni o'chirish"),
)
class RoleViewSet(viewsets.ModelViewSet):
    """
    Rollar (Role) CRUD amallari.
    """
    queryset = Role.objects.prefetch_related('permissions').all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['-id']


@extend_schema(
    tags=['Rollar va Ruxsatlar'],
    summary="Mavjud Django ruxsatlari ro'yxati (Permissions)",
    description="Tizimdagi barcha mavjud Permission'lar ro'yxati. Rolga biriktirish uchun ishlatiladi."
)
class PermissionListView(generics.ListAPIView):
    queryset = Permission.objects.select_related('content_type').order_by('content_type__app_label', 'codename')
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'codename', 'content_type__app_label', 'content_type__model']
    pagination_class = None  # Barcha ruxsatlarni bir vaqtda olish qulay bo'lishi uchun


# ==============================================================================
# Foydalanuvchilar Boshqaruvi View'lari
# ==============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Foydalanuvchilar boshqaruvi'], summary="Foydalanuvchilar ro'yxati"),
    create=extend_schema(tags=['Foydalanuvchilar boshqaruvi'], summary="Yangi foydalanuvchi yaratish"),
    retrieve=extend_schema(tags=['Foydalanuvchilar boshqaruvi'], summary="Foydalanuvchi tafsilotlari"),
    update=extend_schema(tags=['Foydalanuvchilar boshqaruvi'], summary="Foydalanuvchini to'liq yangilash"),
    partial_update=extend_schema(tags=['Foydalanuvchilar boshqaruvi'], summary="Foydalanuvchini qisman yangilash"),
    destroy=extend_schema(tags=['Foydalanuvchilar boshqaruvi'], summary="Foydalanuvchini o'chirish"),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    Foydalanuvchilar (User) boshqaruvi CRUD amallari.
    """
    queryset = User.objects.select_related('role', 'employee', 'employee__position').prefetch_related('role__permissions', 'user_permissions').all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'employee', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee__name']
    ordering_fields = ['id', 'username', 'created_at', 'last_login']
    ordering = ['-id']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'set_password':
            return AdminSetPasswordSerializer
        return UserDetailSerializer

    @extend_schema(
        tags=['Foydalanuvchilar boshqaruvi'],
        summary="Admin: Foydalanuvchi parolini o'rnatish/yangilash",
        description="Admin istalgan foydalanuvchiga yangi parol o'rnatishi mumkin.",
        request=AdminSetPasswordSerializer,
    )
    @action(detail=True, methods=['post'], url_path='set-password')
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = AdminSetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(
            {"detail": f"'{user.username}' foydalanuvchisi paroli muvaffaqiyatli yangilandi."},
            status=status.HTTP_200_OK
        )

