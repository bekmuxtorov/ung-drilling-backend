import logging
from decimal import Decimal
from datetime import datetime, date
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import AuditLog, AuditAction
from .context import get_current_audit_context, get_client_ip, get_client_mac

logger = logging.getLogger('apps.common.audit')

AUDIT_EXCLUDED_APPS = {'contenttypes', 'sessions', 'admin', 'auth'}
AUDIT_EXCLUDED_MODELS = {'auditlog', 'logentry', 'permission'}
AUDIT_INCLUDED_APPS = {'accounts', 'directory', 'operations'}


def should_audit_model(model_cls):
    """Qaysi modellar audit qilinishi kerakligini tekshiradi."""
    app_label = model_cls._meta.app_label
    model_name = model_cls._meta.model_name
    if app_label in AUDIT_EXCLUDED_APPS or model_name in AUDIT_EXCLUDED_MODELS:
        return False
    return app_label in AUDIT_INCLUDED_APPS


def serialize_instance(instance):
    """
    Model obyektining maydonlarini JSON-xavfsiz lug'at (dict) ko'rinishiga keltiradi.
    """
    data = {}
    for field in instance._meta.fields:
        field_name = field.name
        # Maxfiy parollarni auditga yozmaslik
        if field_name == 'password':
            continue
        try:
            val = getattr(instance, field.attname)
            if isinstance(val, (datetime, date)):
                val = val.isoformat()
            elif isinstance(val, Decimal):
                val = float(val)
            elif isinstance(val, (int, float, str, bool)) or val is None:
                pass
            else:
                val = str(val)
            data[field_name] = val
        except Exception:
            pass
    return data


def create_audit_record(instance, action, old_values, new_values, changes):
    """
    AuditLog yozuvini yaratadi.
    Mijoz ma'lumotlarini (User, IP, MAC ID) kontekstdan oladi.
    """
    ctx = get_current_audit_context() or {}
    request = ctx.get('request')

    user = None
    username = ""
    user_full_name = ""
    ip_address = None
    mac_address = ""
    user_agent = ""

    if request:
        req_user = getattr(request, 'user', None)
        if req_user and req_user.is_authenticated:
            user = req_user
            username = req_user.username
            user_full_name = getattr(req_user, 'get_full_name', lambda: '')() or getattr(req_user, 'name', '') or username

        ip_address = get_client_ip(request)
        mac_address = get_client_mac(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
    else:
        username = "system"
        user_full_name = "Tizim / Shell jarayoni"

    AuditLog.objects.create(
        user=user,
        username=username,
        user_full_name=user_full_name,
        ip_address=ip_address,
        mac_address=mac_address,
        user_agent=user_agent,
        action=action,
        app_label=instance._meta.app_label,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance)[:500],
        changes=changes,
        old_values=old_values,
        new_values=new_values,
    )


@receiver(pre_save)
def audit_pre_save_handler(sender, instance, **kwargs):
    """Tahrirlashdan oldingi eski qiymatlarni eslab qolish."""
    if not should_audit_model(sender):
        return

    if instance.pk:
        try:
            old_obj = sender.objects.filter(pk=instance.pk).first()
            if old_obj:
                instance._audit_old_values = serialize_instance(old_obj)
        except Exception as e:
            logger.debug("pre_save audit xatosi: %s", e)


@receiver(post_save)
def audit_post_save_handler(sender, instance, created, **kwargs):
    """Yangi yaratish yoki tahrirlash o'zgarishlarini qayd qilish."""
    if not should_audit_model(sender):
        return

    try:
        new_values = serialize_instance(instance)
        if created:
            action = AuditAction.CREATE
            old_values = {}
            changes = {k: {'old': None, 'new': v} for k, v in new_values.items()}
        else:
            action = AuditAction.UPDATE
            old_values = getattr(instance, '_audit_old_values', {})
            changes = {}
            for k, v in new_values.items():
                if k in {'updated_at', 'created_at'}:
                    continue
                old_v = old_values.get(k)
                if old_v != v:
                    changes[k] = {'old': old_v, 'new': v}

            # Agar hech qanday maydon o'zgarmagan bo'lsa, audit logni ortiqcha to'ldirmaymiz
            if not changes:
                return

        create_audit_record(
            instance=instance,
            action=action,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
        )
    except Exception as e:
        logger.exception("post_save audit xatosi: %s", e)


@receiver(post_delete)
def audit_post_delete_handler(sender, instance, **kwargs):
    """Obyekt o'chirilganda eski qiymatlarini qayd qilish."""
    if not should_audit_model(sender):
        return

    try:
        old_values = getattr(instance, '_audit_old_values', None) or serialize_instance(instance)
        changes = {k: {'old': v, 'new': None} for k, v in old_values.items()}
        create_audit_record(
            instance=instance,
            action=AuditAction.DELETE,
            old_values=old_values,
            new_values={},
            changes=changes,
        )
    except Exception as e:
        logger.exception("post_delete audit xatosi: %s", e)
