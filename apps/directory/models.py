from django.db import models
from apps.common.models import TimeStampedModel


class OperationStageType(models.TextChoices):
    """
    Operatsiya bosqichlari (Enum).
    Demontaj, Tashish, Montaj bosqichlari uchun.
    """
    DISMANTLING = "dismantling", "Demontaj"
    TRANSPORTATION = "transportation", "Tashish"
    INSTALLATION = "installation", "Montaj"


class Enterprise(TimeStampedModel):
    """
    Korxona (Enterprise) modeli.
    """
    name = models.CharField(max_length=255, db_index=True, verbose_name="Korxona nomi")

    class Meta:
        verbose_name = "Korxona"
        verbose_name_plural = "Korxonalar"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class DrillingRigType(TimeStampedModel):
    """
    Burg'ulash uskunasi turi (Drilling Rig Type).
    """
    name = models.CharField(max_length=255, db_index=True, verbose_name="Uskuna turi nomi")

    class Meta:
        verbose_name = "Burg'ulash uskunasi turi"
        verbose_name_plural = "Burg'ulash uskunasi turlari"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Region(TimeStampedModel):
    """
    Viloyat / Hudud (Region) modeli.
    """
    name = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="Hudud nomi")

    class Meta:
        verbose_name = "Hudud"
        verbose_name_plural = "Hududlar"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Area(TimeStampedModel):
    """
    Maydon / Kon (Area) modeli. Region bilan One-to-Many munosabatda.
    """
    name = models.CharField(max_length=255, db_index=True, verbose_name="Maydon nomi")
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="areas",
        verbose_name="Tegishli hudud"
    )

    class Meta:
        verbose_name = "Maydon"
        verbose_name_plural = "Maydonlar"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["region", "name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class Foreman(TimeStampedModel):
    """
    Usta / Prorab (Foreman) modeli.
    """
    name = models.CharField(max_length=255, db_index=True, verbose_name="F.I.SH")
    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Telefon raqami"
    )

    class Meta:
        verbose_name = "Usta (Foreman)"
        verbose_name_plural = "Ustalar (Foremen)"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class TransportType(TimeStampedModel):
    """
    Transport vositasi turi (Transport Type).
    """
    name = models.CharField(max_length=255, db_index=True, verbose_name="Transport turi nomi")

    class Meta:
        verbose_name = "Transport turi"
        verbose_name_plural = "Transport turlari"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Position(TimeStampedModel):
    """
    Lavozim (Position) modeli.
    """
    name = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="Lavozim nomi")

    class Meta:
        verbose_name = "Lavozim"
        verbose_name_plural = "Lavozimlar"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Employee(TimeStampedModel):
    """
    Xodim (Employee) modeli. Position bilan bog'langan.
    """
    name = models.CharField(max_length=255, db_index=True, verbose_name="Xodim F.I.SH")
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Telefon raqami"
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name="employees",
        verbose_name="Lavozimi"
    )

    class Meta:
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["position", "name"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.position.name}"
