from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission


class RoleModelBackend(ModelBackend):
    """
    Foydalanuvchi roli (Role) va unga biriktirilgan ruxsatnomalarni (permissions)
    Django standart autentifikatsiya va ruxsat tizimi (has_perm, get_all_permissions)
    bilan to'liq integratsiya qiluvchi backend.
    """

    def _get_role_permissions(self, user_obj):
        if hasattr(user_obj, 'role') and user_obj.role:
            return user_obj.role.permissions.select_related('content_type').all()
        return Permission.objects.none()

    def get_role_permissions(self, user_obj, obj=None):
        """
        Foydalanuvchining roli orqali ega bo'lgan ruxsatnomalari to'plami (set).
        Format: {'app_label.codename', ...}
        """
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        if not hasattr(user_obj, '_role_perm_cache'):
            perms = self._get_role_permissions(user_obj)
            user_obj._role_perm_cache = {
                f"{p.content_type.app_label}.{p.codename}" for p in perms
            }
        return user_obj._role_perm_cache

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            perms = super().get_all_permissions(user_obj, obj)
            role_perms = self.get_role_permissions(user_obj, obj)
            user_obj._perm_cache = perms | role_perms
        return user_obj._perm_cache

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        return perm in self.get_all_permissions(user_obj, obj)
