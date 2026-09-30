from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    CurrentUserView,
    ChangePasswordView,
    RoleViewSet,
    PermissionListView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # JWT Autentifikatsiya endpointlari
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
    
    # Joriy foydalanuvchi va parol boshqaruvi
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Ruxsatlar (Permissions)
    path('permissions/', PermissionListView.as_view(), name='permissions_list'),

    # Rollar va Foydalanuvchilar CRUD
    path('', include(router.urls)),
]
