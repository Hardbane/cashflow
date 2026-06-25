# Generated manually for the test task project.
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CashFlowType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Название')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
            ],
            options={
                'verbose_name': 'Тип операции',
                'verbose_name_plural': 'Типы операций',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Название')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
            ],
            options={
                'verbose_name': 'Статус',
                'verbose_name_plural': 'Статусы',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Название')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='categories', to='ledger.cashflowtype', verbose_name='Тип операции')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Название')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subcategories', to='ledger.category', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Подкатегория',
                'verbose_name_plural': 'Подкатегории',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='CashFlowRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_date', models.DateField(default=django.utils.timezone.localdate, verbose_name='Дата записи')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(0.01)], verbose_name='Сумма, ₽')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='records', to='ledger.category', verbose_name='Категория')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='records', to='ledger.status', verbose_name='Статус')),
                ('subcategory', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='records', to='ledger.subcategory', verbose_name='Подкатегория')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='records', to='ledger.cashflowtype', verbose_name='Тип операции')),
            ],
            options={
                'verbose_name': 'Запись ДДС',
                'verbose_name_plural': 'Записи ДДС',
                'ordering': ('-record_date', '-created_at'),
            },
        ),
        migrations.AddConstraint(
            model_name='cashflowtype',
            constraint=models.UniqueConstraint(fields=('name',), name='unique_cashflow_type_name'),
        ),
        migrations.AddConstraint(
            model_name='status',
            constraint=models.UniqueConstraint(fields=('name',), name='unique_status_name'),
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('type', 'name'), name='unique_category_per_type'),
        ),
        migrations.AddConstraint(
            model_name='subcategory',
            constraint=models.UniqueConstraint(fields=('category', 'name'), name='unique_subcategory_per_cat'),
        ),
        migrations.AddIndex(
            model_name='cashflowrecord',
            index=models.Index(fields=['record_date'], name='cashrec_date_idx'),
        ),
        migrations.AddIndex(
            model_name='cashflowrecord',
            index=models.Index(fields=['status'], name='cashrec_status_idx'),
        ),
        migrations.AddIndex(
            model_name='cashflowrecord',
            index=models.Index(fields=['type'], name='cashrec_type_idx'),
        ),
        migrations.AddIndex(
            model_name='cashflowrecord',
            index=models.Index(fields=['category'], name='cashrec_category_idx'),
        ),
        migrations.AddIndex(
            model_name='cashflowrecord',
            index=models.Index(fields=['subcategory'], name='cashrec_subcat_idx'),
        ),
    ]
