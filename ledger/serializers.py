from rest_framework import serializers
from .models import CashFlowRecord, CashFlowType, Category, Status, SubCategory


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']


class CashFlowTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashFlowType
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'type_name', 'is_active', 'created_at', 'updated_at']


class SubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    type_id = serializers.IntegerField(source='category.type_id', read_only=True)
    type_name = serializers.CharField(source='category.type.name', read_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'category', 'category_name', 'type_id', 'type_name', 'is_active', 'created_at', 'updated_at']


class CashFlowRecordSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source='status.name', read_only=True)
    type_name = serializers.CharField(source='type.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)

    class Meta:
        model = CashFlowRecord
        fields = [
            'id', 'record_date', 'status', 'status_name', 'type', 'type_name', 'category',
            'category_name', 'subcategory', 'subcategory_name', 'amount', 'comment',
            'created_at', 'updated_at',
        ]

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        type_obj = attrs.get('type') or (instance.type if instance else None)
        category = attrs.get('category') or (instance.category if instance else None)
        subcategory = attrs.get('subcategory') or (instance.subcategory if instance else None)

        if category and type_obj and category.type_id != type_obj.id:
            raise serializers.ValidationError({'category': 'Категория не относится к выбранному типу операции.'})
        if subcategory and category and subcategory.category_id != category.id:
            raise serializers.ValidationError({'subcategory': 'Подкатегория не связана с выбранной категорией.'})
        return attrs
