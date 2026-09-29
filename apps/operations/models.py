from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import TimeStampedModel
from apps.directory.models import (
    Enterprise,
    DrillingRigType,
    Area,
    Foreman,
    TransportType,
    OperationStageType,
)


class DerrickErectionOperation(TimeStampedModel):
    """
    Vishka-montaj (VBM) operatsiyasi modeli.
    Burg'ulash uskunasini bir maydondan ikkinchisiga ko'chirish va montaj qilish ishlari.
    """
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.PROTECT,
        related_name='operations',
        verbose_name="Korxona"
    )
    drilling_rig_type = models.ForeignKey(
        DrillingRigType,
        on_delete=models.PROTECT,
        related_name='operations',
        verbose_name="Burg'ulash uskunasi turi"
    )
    from_area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name='operations_from',
        verbose_name="Qaysi maydondan"
    )
    from_well_number = models.CharField(
        max_length=50,
        verbose_name="Qaysi quduqdan (№)"
    )
    to_area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name='operations_to',
        verbose_name="Qaysi maydonga"
    )
    to_well_number = models.CharField(
        max_length=50,
        verbose_name="Qaysi quduqqa (№)"
    )
    foreman = models.ForeignKey(
        Foreman,
        on_delete=models.PROTECT,
        related_name='operations',
        verbose_name="Usta (Prorab)"
    )
    number_employees = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Ishchilar soni"
    )
    distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Masofa (km)"
    )
    plan_days = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Rejadagi kunlar"
    )
    expected_drilling_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Kutilayotgan burg'ulash boshlanish sanasi"
    )
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        verbose_name="Bajarilish foizi (%)"
    )
    delay_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name="Kechikish sababi"
    )
    work_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Bajarilayotgan ish tavsifi"
    )

    class Meta:
        verbose_name = "VBM Operatsiyasi"
        verbose_name_plural = "VBM Operatsiyalari"
        ordering = ['-id']
        indexes = [
            models.Index(fields=['enterprise', 'foreman']),
            models.Index(fields=['from_area', 'to_area']),
            models.Index(fields=['completion_percentage']),
        ]

    def __str__(self):
        return (
            f"VBM #{self.id}: {self.from_area.name} (№{self.from_well_number}) -> "
            f"{self.to_area.name} (№{self.to_well_number})"
        )


class OperationStage(TimeStampedModel):
    """
    Operatsiya bosqichlari modeli (Demontaj, Tashish, Montaj).
    Rejadagi va amaldagi kunlar, sanalar.
    """
    operation = models.ForeignKey(
        DerrickErectionOperation,
        on_delete=models.CASCADE,
        related_name='stages',
        verbose_name="Operatsiya"
    )
    stage_type = models.CharField(
        max_length=50,
        choices=OperationStageType.choices,
        verbose_name="Bosqich turi"
    )
    plan_days = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Reja kun"
    )
    fact_days = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Fakt kun"
    )
    plan_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Rejadagi boshlanish sanasi"
    )
    plan_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Rejadagi tugash sanasi"
    )
    fact_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Amaldagi boshlanish sanasi"
    )
    fact_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Amaldagi tugash sanasi"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Izoh / Tavsif"
    )

    class Meta:
        verbose_name = "Operatsiya bosqichi"
        verbose_name_plural = "Operatsiya bosqichlari"
        ordering = ['id']
        indexes = [
            models.Index(fields=['operation', 'stage_type']),
        ]

    def __str__(self):
        return f"{self.operation} - {self.get_stage_type_display()}"


class DailyWorkDescription(TimeStampedModel):
    """
    Kunlik bajarilgan ish tavsifi (hisoboti).
    """
    derrick_erection_operation = models.ForeignKey(
        DerrickErectionOperation,
        on_delete=models.CASCADE,
        related_name='daily_works',
        verbose_name="VBM Operatsiyasi"
    )
    description = models.TextField(
        verbose_name="Kunlik ish tavsifi"
    )

    class Meta:
        verbose_name = "Kunlik ish hisoboti"
        verbose_name_plural = "Kunlik ish hisobotlari"
        ordering = ['-created_at']

    def __str__(self):
        return f"Kunlik hisobot #{self.id} (Operatsiya #{self.derrick_erection_operation_id})"


class DailyTransportItem(TimeStampedModel):
    """
    Kunlik hisobotga biriktirilgan transport vositalari va ularning soni.
    """
    daily_work_description = models.ForeignKey(
        DailyWorkDescription,
        on_delete=models.CASCADE,
        related_name='transport_items',
        verbose_name="Kunlik ish hisoboti"
    )
    transport_type = models.ForeignKey(
        TransportType,
        on_delete=models.PROTECT,
        related_name='daily_transport_items',
        verbose_name="Transport turi"
    )
    count = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Transport vositalari soni"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Transport bo'yicha izoh"
    )

    class Meta:
        verbose_name = "Kunlik transport vositasi"
        verbose_name_plural = "Kunlik transport vositalari"
        ordering = ['-id']

    def __str__(self):
        return f"{self.transport_type.name}: {self.count} ta (Hisobot #{self.daily_work_description_id})"
