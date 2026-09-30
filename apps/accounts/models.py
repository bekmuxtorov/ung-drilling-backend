from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.core import validators
from django.utils.deconstruct import deconstructible
from apps.common.models import TimeStampedModel


@deconstructible
class SpaceAllowedUsernameValidator(validators.RegexValidator):
    """
    Username maydonida harflar, raqamlar, probel (bo'sh joy) hamda @/./+/-/_ belgilariga
    ruxsat beruvchi validator.
    """
    regex = r"^[\w.@+ -]+\Z"
    message = (
        "Yaroqli foydalanuvchi nomini kiriting. Ushbu qiymat faqat harflar, "
        "raqamlar, probel (bo'sh joy) va @/./+/-/_ belgilaridan iborat bo'lishi mumkin."
    )
    flags = 0


class Role(TimeStampedModel):
    """
    Tizim rollari (Role) modeli.
    Har bir rolga Django'ning default Permission obyektlari biriktiriladi.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="Rol nomi"
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="roles",
        verbose_name="Ruxsatlar"
    )

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Rollar"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class User(AbstractUser, TimeStampedModel):
    """
    Tizim foydalanuvchisi (User) modeli.
    Django standart foydalanuvchisini (AbstractUser) kengaytiradi va
    Employee (Xodim) hamda Role (Rol) bilan bog'laydi.
    Username'da bo'sh joy (probel) bo'lishiga ruxsat beradi.
    """
    username_validator = SpaceAllowedUsernameValidator()

    username = models.CharField(
        "Foydalanuvchi nomi",
        max_length=150,
        unique=True,
        help_text=(
            "Majburiy. 150 ta yoki undan kam belgilar. Harflar, raqamlar, "
            "probel (bo'sh joy) va @/./+/-/_ belgilariga ruxsat beriladi."
        ),
        validators=[username_validator],
        error_messages={
            "unique": "Bu nomdagi foydalanuvchi allaqachon mavjud.",
        },
    )
    employee = models.ForeignKey(
        'directory.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Xodim"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Rol"
    )

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ["-id"]

    def __str__(self):
        return self.username

    @property
    def role_name(self):
        return self.role.name if self.role else None

    @property
    def employee_name(self):
        return self.employee.name if self.employee else None

    def get_all_permissions_list(self):
        """
        Foydalanuvchining barcha ruxsatnomalarini (format: 'app_label.codename') ro'yxat ko'rinishida qaytaradi.
        """
        if not self.is_active:
            return []
        if self.is_superuser:
            perms = Permission.objects.select_related('content_type').all()
            return [f"{p.content_type.app_label}.{p.codename}" for p in perms]
        return sorted(list(self.get_all_permissions()))

