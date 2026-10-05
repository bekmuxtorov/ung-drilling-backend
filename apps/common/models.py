from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    """
    Barcha modellar uchun umumiy vaqt maydonlari (created_at, updated_at).
    DRY (Don't Repeat Yourself) tamoyiliga muvofiq yaratilgan abstrakt model.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Yaratilgan vaqti"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Tahrirlangan vaqti"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class AuditAction(models.TextChoices):
    CREATE = 'create', 'Yaratish'
    UPDATE = 'update', 'Tahrirlash'
    DELETE = 'delete', "O'chirish"


class AuditLog(models.Model):
    """
    Tizimdagi barcha o'zgarishlar (Audit Trail) qaydnomasi.
    Qaysi foydalanuvchi, qaysi IP manzil va MAC ID orqali qanday o'zgarish
    qilganligini (eski qiymatlar, yangi qiymatlar, diff) saqlaydi.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name="Foydalanuvchi"
    )
    username = models.CharField(
        max_length=150,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Foydalanuvchi nomi"
    )
    user_full_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Foydalanuvchi F.I.SH"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="IP manzil"
    )
    mac_address = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        verbose_name="MAC ID / Qurilma ID"
    )
    user_agent = models.TextField(
        blank=True,
        default="",
        verbose_name="User Agent"
    )
    action = models.CharField(
        max_length=20,
        choices=AuditAction.choices,
        db_index=True,
        verbose_name="Harakat turi"
    )
    app_label = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Ilova (App)"
    )
    model_name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Model nomi"
    )
    object_id = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="Obyekt ID"
    )
    object_repr = models.CharField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="Obyekt qisqa matni"
    )
    changes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="O'zgarishlar (Diff: eski va yangi)"
    )
    old_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Eski qiymatlar"
    )
    new_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Yangi qiymatlar"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Qayd etilgan vaqt"
    )

    class Meta:
        verbose_name = "Audit log"
        verbose_name_plural = "Audit loglari"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['mac_address', 'created_at']),
        ]

    def __str__(self):
        user_display = self.username or "Tizim (Anonim)"
        return f"[{self.get_action_display()}] {self.model_name} #{self.object_id} - {user_display} ({self.created_at:%Y-%m-%d %H:%M})"
