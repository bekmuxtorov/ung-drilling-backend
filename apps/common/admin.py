import json
from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_at',
        'action_badge',
        'model_name',
        'object_id',
        'username',
        'ip_address',
        'mac_address',
        'short_object_repr',
    )
    list_filter = (
        'action',
        'model_name',
        'app_label',
        'created_at',
    )
    search_fields = (
        'username',
        'user_full_name',
        'model_name',
        'object_id',
        'object_repr',
        'ip_address',
        'mac_address',
    )
    readonly_fields = (
        'id',
        'user',
        'username',
        'user_full_name',
        'ip_address',
        'mac_address',
        'user_agent',
        'action',
        'app_label',
        'model_name',
        'object_id',
        'object_repr',
        'pretty_changes',
        'pretty_old_values',
        'pretty_new_values',
        'created_at',
    )
    ordering = ('-created_at',)
    list_per_page = 30

    fieldsets = (
        ("Foydalanuvchi va Qurilma", {
            'fields': (
                ('user', 'username', 'user_full_name'),
                ('ip_address', 'mac_address'),
                'user_agent',
            )
        }),
        ("Obyekt va Harakat", {
            'fields': (
                ('action', 'app_label', 'model_name'),
                ('object_id', 'object_repr'),
                'created_at',
            )
        }),
        ("O'zgarishlar (Diff, Eski va Yangi qiymatlar)", {
            'fields': (
                'pretty_changes',
                'pretty_old_values',
                'pretty_new_values',
            )
        }),
    )

    def has_add_permission(self, request):
        """Audit loglariga qo'lda yozuv qo'shish qat'iyan man etiladi."""
        return False

    def has_change_permission(self, request, obj=None):
        """Audit loglarini tahrirlash qat'iyan man etiladi (WORM)."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Audit loglarini o'chirish qat'iyan man etiladi."""
        return False

    @admin.display(description="Harakat")
    def action_badge(self, obj):
        colors = {
            'create': '#10b981',  # Yashil
            'update': '#3b82f6',  # Ko'k
            'delete': '#ef4444',  # Qizil
        }
        color = colors.get(obj.action, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 11px;">{}</span>',
            color,
            obj.get_action_display()
        )

    @admin.display(description="Obyekt matni")
    def short_object_repr(self, obj):
        if len(obj.object_repr) > 40:
            return obj.object_repr[:40] + "..."
        return obj.object_repr

    @admin.display(description="O'zgarishlar (Diff)")
    def pretty_changes(self, obj):
        if not obj.changes:
            return "—"
        return format_html(
            '<pre style="background: #1e293b; color: #f8fafc; padding: 10px; border-radius: 6px; font-size: 12px; max-height: 350px; overflow: auto;">{}</pre>',
            json.dumps(obj.changes, ensure_ascii=False, indent=2)
        )

    @admin.display(description="Eski qiymatlar")
    def pretty_old_values(self, obj):
        if not obj.old_values:
            return "—"
        return format_html(
            '<pre style="background: #1e293b; color: #f8fafc; padding: 10px; border-radius: 6px; font-size: 12px; max-height: 250px; overflow: auto;">{}</pre>',
            json.dumps(obj.old_values, ensure_ascii=False, indent=2)
        )

    @admin.display(description="Yangi qiymatlar")
    def pretty_new_values(self, obj):
        if not obj.new_values:
            return "—"
        return format_html(
            '<pre style="background: #1e293b; color: #f8fafc; padding: 10px; border-radius: 6px; font-size: 12px; max-height: 250px; overflow: auto;">{}</pre>',
            json.dumps(obj.new_values, ensure_ascii=False, indent=2)
        )
