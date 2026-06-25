from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class NamedModel(models.Model):
    """Базовая модель для справочников с уникальным названием."""

    name = models.CharField('Название', max_length=120)
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Status(NamedModel):
    class Meta(NamedModel.Meta):
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        constraints = [models.UniqueConstraint(fields=['name'], name='unique_status_name')]


class CashFlowType(NamedModel):
    class Meta(NamedModel.Meta):
        verbose_name = 'Тип операции'
        verbose_name_plural = 'Типы операций'
        constraints = [models.UniqueConstraint(fields=['name'], name='unique_cashflow_type_name')]


class Category(NamedModel):
    type = models.ForeignKey(
        CashFlowType,
        verbose_name='Тип операции',
        on_delete=models.PROTECT,
        related_name='categories',
    )

    class Meta(NamedModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        constraints = [
            models.UniqueConstraint(fields=['type', 'name'], name='unique_category_per_type'),
        ]

    def __str__(self) -> str:
        return f'{self.name} ({self.type.name})'


class SubCategory(NamedModel):
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.PROTECT,
        related_name='subcategories',
    )

    class Meta(NamedModel.Meta):
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        constraints = [
            models.UniqueConstraint(fields=['category', 'name'], name='unique_subcategory_per_cat'),
        ]

    def __str__(self) -> str:
        return f'{self.name} ({self.category.name})'


class CashFlowRecord(models.Model):
    record_date = models.DateField('Дата записи', default=timezone.localdate)
    status = models.ForeignKey(
        Status,
        verbose_name='Статус',
        on_delete=models.PROTECT,
        related_name='records',
    )
    type = models.ForeignKey(
        CashFlowType,
        verbose_name='Тип операции',
        on_delete=models.PROTECT,
        related_name='records',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.PROTECT,
        related_name='records',
    )
    subcategory = models.ForeignKey(
        SubCategory,
        verbose_name='Подкатегория',
        on_delete=models.PROTECT,
        related_name='records',
    )
    amount = models.DecimalField(
        'Сумма, ₽',
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Запись ДДС'
        verbose_name_plural = 'Записи ДДС'
        ordering = ('-record_date', '-created_at')
        indexes = [
            models.Index(fields=['record_date']),
            models.Index(fields=['status']),
            models.Index(fields=['type']),
            models.Index(fields=['category']),
            models.Index(fields=['subcategory']),
        ]

    def __str__(self) -> str:
        return f'{self.record_date:%d.%m.%Y} — {self.type.name} — {self.amount} ₽'

    def clean(self) -> None:
        errors: dict[str, str] = {}
        if self.category_id and self.type_id and self.category.type_id != self.type_id:
            errors['category'] = 'Категория не относится к выбранному типу операции.'
        if self.subcategory_id and self.category_id and self.subcategory.category_id != self.category_id:
            errors['subcategory'] = 'Подкатегория не связана с выбранной категорией.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
