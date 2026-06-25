from django.contrib import admin
from .models import CashFlowRecord, CashFlowType, Category, Status, SubCategory


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active',)


@admin.register(CashFlowType)
class CashFlowTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'type__name')
    list_filter = ('type', 'is_active')


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_type', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'category__name', 'category__type__name')
    list_filter = ('category__type', 'category', 'is_active')

    @admin.display(description='Тип')
    def get_type(self, obj):
        return obj.category.type


@admin.register(CashFlowRecord)
class CashFlowRecordAdmin(admin.ModelAdmin):
    list_display = ('record_date', 'status', 'type', 'category', 'subcategory', 'amount', 'short_comment')
    list_filter = ('record_date', 'status', 'type', 'category', 'subcategory')
    search_fields = ('comment',)
    date_hierarchy = 'record_date'

    @admin.display(description='Комментарий')
    def short_comment(self, obj):
        return (obj.comment[:60] + '…') if len(obj.comment) > 60 else obj.comment
