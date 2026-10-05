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
    Employee,
    MachineType,
    DepthsLayers,
    Resources,
    Unit,
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


class WellDesignType(models.TextChoices):
    PLAN = "plan", "Reja"
    FACT = "fact", "Fakt"


class WellDesignPeriodType(models.TextChoices):
    DAY = "day", "Kunlik"
    MONTH = "month", "Oylik"
    YEAR = "year", "Yillik"


class DrillingBPA(TimeStampedModel):
    """
    Burg'ulash (BPA) operatsiyasi modeli.
    Quduqlarni burg'ulash jarayoni, pudrat akti va unga tegishli texnik ko'rsatkichlar.
    """
    number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        verbose_name="BPA / Shartnoma raqami"
    )
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.PROTECT,
        related_name="drilling_bpas",
        verbose_name="Korxona"
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="drilling_bpas",
        verbose_name="Mas'ul xodim"
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="drilling_bpas",
        verbose_name="Maydon / Kon"
    )
    well_number = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="Quduq raqami (№)"
    )
    machine_type = models.ForeignKey(
        MachineType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="drilling_bpas",
        verbose_name="Mashina / Mexanizm turi"
    )
    drilling_start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Burg'ulash boshlanish vaqti"
    )
    depth_plan = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Rejadagi umumiy chuqurlik (m)"
    )

    class Meta:
        verbose_name = "Burg'ulash (BPA) operatsiyasi"
        verbose_name_plural = "Burg'ulash (BPA) operatsiyalari"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["enterprise", "well_number"]),
            models.Index(fields=["area", "well_number"]),
        ]

    def __str__(self):
        area_name = self.area.name if self.area else "Noma'lum maydon"
        return f"BPA №{self.number or self.id} ({area_name}, Quduq №{self.well_number})"

    @property
    def current_depth(self) -> float:
        """
        Kunlik hisobotlar bo'yicha umumiy erishilgan chuqurlik.
        1) WellDesignInLength kunlik ('day') faktik uzunliklar (length_fact) yig'indisi.
        2) Agar kunlik bo'lmasa, barcha faktik uzunliklar yig'indisi.
        3) Agar u ham bo'lmasa, WellDesign (fact) yoki qatlamlar yig'indisi.
        """
        day_sum = self.well_designs_in_length.filter(type=WellDesignPeriodType.DAY).aggregate(
            total=models.Sum("length_fact")
        )["total"]
        if day_sum is not None and day_sum > 0:
            return round(float(day_sum), 2)

        total_lengths = self.well_designs_in_length.aggregate(
            total=models.Sum("length_fact")
        )["total"]
        if total_lengths is not None and total_lengths > 0:
            return round(float(total_lengths), 2)

        fact_design = self.well_designs.filter(type=WellDesignType.FACT).aggregate(
            total=models.Sum("length")
        )["total"]
        if fact_design is not None and fact_design > 0:
            return round(float(fact_design), 2)

        layer_sum = self.depths_layers_lengths.aggregate(
            total=models.Sum("length")
        )["total"]
        if layer_sum is not None and layer_sum > 0:
            return round(float(layer_sum), 2)

        return 0.0

    @property
    def current_dept(self) -> float:
        """current_depth uchun alias."""
        return self.current_depth


class WellDesign(TimeStampedModel):
    """
    Quduq konstruksiyasi (Well Design).
    Reja va fakt bo'yicha quvur diametri va chuqurligi/uzunligi.
    """
    drilling_bpa = models.ForeignKey(
        DrillingBPA,
        on_delete=models.CASCADE,
        related_name="well_designs",
        verbose_name="Burg'ulash BPA"
    )
    type = models.CharField(
        max_length=10,
        choices=WellDesignType.choices,
        default=WellDesignType.PLAN,
        verbose_name="Turi (Reja/Fakt)"
    )
    pipe_diameter = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        verbose_name="Quvur diametri (mm)"
    )
    length = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        verbose_name="Uzunligi / Chuqurligi (m)"
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Boshlanish sanasi va vaqti"
    )

    class Meta:
        verbose_name = "Quduq konstruksiyasi"
        verbose_name_plural = "Quduq konstruksiyalari"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["drilling_bpa", "type"]),
        ]

    def __str__(self):
        return f"Konstruksiya #{self.id} ({self.get_type_display()}, d={self.pipe_diameter}mm, L={self.length}m)"


class WellDesignInLength(TimeStampedModel):
    """
    Quduq o'tish dinamikasi (Well Design In Length).
    Kunlik, oylik va yillik reja hamda faktik o'tish ko'rsatkichlari.
    """
    drilling_bpa = models.ForeignKey(
        DrillingBPA,
        on_delete=models.CASCADE,
        related_name="well_designs_in_length",
        verbose_name="Burg'ulash BPA"
    )
    type = models.CharField(
        max_length=10,
        choices=WellDesignPeriodType.choices,
        default=WellDesignPeriodType.DAY,
        verbose_name="Davr turi (kun/oy/yil)"
    )
    length_plan = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        verbose_name="Reja bo'yicha uzunlik (m)"
    )
    length_fact = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        verbose_name="Fakt bo'yicha uzunlik (m)"
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Boshlanish sanasi va vaqti"
    )

    class Meta:
        verbose_name = "Quduq o'tish dinamikasi (uzunlik bo'yicha)"
        verbose_name_plural = "Quduq o'tish dinamikasi (uzunlik bo'yicha)"
        ordering = ["-start_date", "-id"]
        indexes = [
            models.Index(fields=["drilling_bpa", "type"]),
        ]

    def __str__(self):
        return f"{self.get_type_display()} o'tish #{self.id} (Reja: {self.length_plan}m, Fakt: {self.length_fact}m)"

    @property
    def delta(self) -> float:
        """Reja va fakt o'rtasidagi farq (fakt - reja)."""
        return round((self.length_fact or 0.0) - (self.length_plan or 0.0), 2)

    @property
    def delta_percent(self) -> float:
        """Rejaga nisbatan farq foizi."""
        if not self.length_plan:
            return 0.0
        return round((self.delta / self.length_plan) * 100, 2)


class DepthsLayersLength(TimeStampedModel):
    """
    Chuqurlik qatlamlari oraliqlari (Depths Layers Length).
    Muayyan qatlamning BPA bo'yicha qalinligi / chuqurlik oralig'i.
    """
    drilling_bpa = models.ForeignKey(
        DrillingBPA,
        on_delete=models.CASCADE,
        related_name="depths_layers_lengths",
        verbose_name="Burg'ulash BPA"
    )
    layer = models.ForeignKey(
        DepthsLayers,
        on_delete=models.PROTECT,
        related_name="depths_layers_lengths",
        verbose_name="Chuqurlik qatlami"
    )
    length = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        verbose_name="Qatlam qalinligi / chuqurligi (m)"
    )

    class Meta:
        verbose_name = "Chuqurlik qatlami oralig'i"
        verbose_name_plural = "Chuqurlik qatlamlari oraliqlari"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["drilling_bpa", "layer"]),
        ]

    def __str__(self):
        return f"{self.layer.name}: {self.length}m (BPA #{self.drilling_bpa_id})"


class DailyWorkDescriptionBPA(TimeStampedModel):
    """
    BPA bo'yicha kunlik ish hisoboti va burg'ulash eritmasi / texnologik parametrlari.
    """
    drilling_bpa = models.ForeignKey(
        DrillingBPA,
        on_delete=models.CASCADE,
        related_name="daily_works",
        verbose_name="Burg'ulash BPA"
    )
    report_date = models.DateField(
        db_index=True,
        verbose_name="Hisobot sanasi"
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Bajarilgan ishlar tavsifi"
    )
    # Eritma va burg'ulash parametrlari
    density = models.FloatField(
        default=0.0,
        verbose_name="Eritma zichligi (g/sm³)"
    )
    viscosity = models.FloatField(
        default=0.0,
        verbose_name="Qovushqoqlik (sek)"
    )
    fluid_loss = models.FloatField(
        default=0.0,
        verbose_name="Suv beruvchanlik (sm³/30daq)"
    )
    mud_cake = models.FloatField(
        default=0.0,
        verbose_name="Gil po'stlog'i (mm)"
    )
    ph_level = models.FloatField(
        default=0.0,
        verbose_name="pH darajasi"
    )
    weight_on_bit = models.FloatField(
        default=0.0,
        verbose_name="Dolotoga tushadigan yuk (tonna)"
    )
    rpm = models.FloatField(
        default=0.0,
        verbose_name="Rotor tezligi (ayl/daq)"
    )
    pump_pressure = models.FloatField(
        default=0.0,
        verbose_name="Nasos bosimi (MPa / bar)"
    )
    flow_rate = models.FloatField(
        default=0.0,
        verbose_name="Eritma sarfi (l/sek)"
    )

    class Meta:
        verbose_name = "BPA kunlik ish hisoboti"
        verbose_name_plural = "BPA kunlik ish hisobotlari"
        ordering = ["-report_date", "-id"]
        indexes = [
            models.Index(fields=["drilling_bpa", "report_date"]),
        ]

    def __str__(self):
        return f"BPA kunlik hisobot: {self.report_date} (BPA #{self.drilling_bpa_id})"


class AvailableResourcesBPA(TimeStampedModel):
    """
    BPA bo'yicha mavjud / ajratilgan resurslar.
    """
    drilling_bpa = models.ForeignKey(
        DrillingBPA,
        on_delete=models.CASCADE,
        related_name="available_resources",
        verbose_name="Burg'ulash BPA"
    )
    resources = models.ForeignKey(
        Resources,
        on_delete=models.PROTECT,
        related_name="available_in_bpas",
        verbose_name="Resurs"
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="available_in_bpas",
        verbose_name="O'lchov birligi"
    )
    value = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        verbose_name="Miqdori / Qiymati"
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Izoh / Tavsif"
    )

    class Meta:
        verbose_name = "BPA mavjud resursi"
        verbose_name_plural = "BPA mavjud resurslari"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["drilling_bpa", "resources"]),
        ]

    def __str__(self):
        return f"{self.resources.name}: {self.value} {self.unit.name} (BPA #{self.drilling_bpa_id})"

