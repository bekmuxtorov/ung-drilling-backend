from rest_framework.permissions import BasePermission


class HasRoleOrModelPermission(BasePermission):
    """
    Foydalanuvchining roli va ruxsatlarini tekshiruvchi DRF permission klassi.
    Superuser uchun har doim to'liq ruxsat beriladi.
    Boshqa foydalanuvchilar uchun mos operatsiya ruxsatnomasi (view, add, change, delete)
    talab qilinadi.
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if getattr(view, '_ignore_model_permissions', False):
            return True

        queryset = getattr(view, 'queryset', None)
        if queryset is None:
            return True

        model_cls = queryset.model
        app_label = model_cls._meta.app_label
        model_name = model_cls._meta.model_name

        perms = self.perms_map.get(request.method, [])
        required_perms = [perm % {'app_label': app_label, 'model_name': model_name} for perm in perms]

        return all(request.user.has_perm(perm) for perm in required_perms)
