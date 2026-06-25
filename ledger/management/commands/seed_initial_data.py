import os
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from ledger.models import CashFlowRecord, CashFlowType, Category, Status, SubCategory


class Command(BaseCommand):
    help = 'Создаёт базовые справочники и, опционально, демо-записи.'

    def handle(self, *args, **options):
        statuses = ['Бизнес', 'Личное', 'Налог']
        for name in statuses:
            Status.objects.get_or_create(name=name, defaults={'is_active': True})

        refill, _ = CashFlowType.objects.get_or_create(name='Пополнение', defaults={'is_active': True})
        withdrawal, _ = CashFlowType.objects.get_or_create(name='Списание', defaults={'is_active': True})

        income_category, _ = Category.objects.get_or_create(
            type=refill,
            name='Доходы',
            defaults={'is_active': True},
        )
        SubCategory.objects.get_or_create(category=income_category, name='Оплата клиентов', defaults={'is_active': True})
        SubCategory.objects.get_or_create(category=income_category, name='Возврат средств', defaults={'is_active': True})

        infrastructure, _ = Category.objects.get_or_create(
            type=withdrawal,
            name='Инфраструктура',
            defaults={'is_active': True},
        )
        marketing, _ = Category.objects.get_or_create(
            type=withdrawal,
            name='Маркетинг',
            defaults={'is_active': True},
        )
        SubCategory.objects.get_or_create(category=infrastructure, name='VPS', defaults={'is_active': True})
        SubCategory.objects.get_or_create(category=infrastructure, name='Proxy', defaults={'is_active': True})
        SubCategory.objects.get_or_create(category=marketing, name='Farpost', defaults={'is_active': True})
        SubCategory.objects.get_or_create(category=marketing, name='Avito', defaults={'is_active': True})

        if os.getenv('SEED_SAMPLE_RECORDS', '0').lower() in {'1', 'true', 'yes', 'on'}:
            business = Status.objects.get(name='Бизнес')
            personal = Status.objects.get(name='Личное')
            vps = SubCategory.objects.get(category=infrastructure, name='VPS')
            avito = SubCategory.objects.get(category=marketing, name='Avito')
            CashFlowRecord.objects.get_or_create(
                record_date=timezone.localdate(),
                status=business,
                type=withdrawal,
                category=infrastructure,
                subcategory=vps,
                amount=Decimal('1200.00'),
                defaults={'comment': 'Оплата VPS'},
            )
            CashFlowRecord.objects.get_or_create(
                record_date=timezone.localdate(),
                status=personal,
                type=withdrawal,
                category=marketing,
                subcategory=avito,
                amount=Decimal('500.00'),
                defaults={'comment': 'Тестовая рекламная кампания'},
            )

        self.stdout.write(self.style.SUCCESS('Базовые справочники ДДС готовы.'))
