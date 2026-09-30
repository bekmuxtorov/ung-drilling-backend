from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'permissions_count', 'created_at', 'updated_at')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)
    readonly_fields = ('created_at', 'updated_at')

    def permissions_count(self, obj):
        return obj.permissions.count()
    permissions_count.short_description = "Ruxsatlar soni"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'employee',
        'role',
        'is_staff',
        'is_active',
        'created_at'
    )
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'employee__name')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Tizim ma'lumotlari (Role va Xodim)", {
            'fields': ('employee', 'role', 'created_at', 'updated_at')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Tizim ma'lumotlari (Role va Xodim)", {
            'fields': ('employee', 'role')
        }),
    )
