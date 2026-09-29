from django.db import models


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
