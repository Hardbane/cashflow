from django import forms
from .models import CashFlowRecord, CashFlowType, Category, Status, SubCategory

BOOTSTRAP_CLASS = 'form-control'
SELECT_CLASS = 'form-select'


class BootstrapModelForm(forms.ModelForm):
    """Добавляет Bootstrap-классы всем полям формы."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', SELECT_CLASS)
            else:
                widget.attrs.setdefault('class', BOOTSTRAP_CLASS)


class CashFlowRecordForm(BootstrapModelForm):
    record_date = forms.DateField(
        label='Дата записи',
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d', '%d.%m.%Y'],
    )

    class Meta:
        model = CashFlowRecord
        fields = ['record_date', 'status', 'type', 'category', 'subcategory', 'amount', 'comment']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Необязательный комментарий'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].queryset = Status.objects.filter(is_active=True)
        self.fields['type'].queryset = CashFlowType.objects.filter(is_active=True)
        self.fields['category'].queryset = Category.objects.filter(is_active=True).select_related('type')
        self.fields['subcategory'].queryset = SubCategory.objects.filter(is_active=True).select_related('category')

        data = self.data if self.is_bound else None
        selected_type = data.get('type') if data else getattr(self.instance, 'type_id', None)
        selected_category = data.get('category') if data else getattr(self.instance, 'category_id', None)

        if selected_type:
            self.fields['category'].queryset = self.fields['category'].queryset.filter(type_id=selected_type)
        else:
            self.fields['category'].queryset = self.fields['category'].queryset.none()

        if selected_category:
            self.fields['subcategory'].queryset = self.fields['subcategory'].queryset.filter(category_id=selected_category)
        else:
            self.fields['subcategory'].queryset = self.fields['subcategory'].queryset.none()

    def clean(self):
        cleaned = super().clean()
        type_obj = cleaned.get('type')
        category = cleaned.get('category')
        subcategory = cleaned.get('subcategory')

        if category and type_obj and category.type_id != type_obj.id:
            self.add_error('category', 'Категория не относится к выбранному типу операции.')
        if subcategory and category and subcategory.category_id != category.id:
            self.add_error('subcategory', 'Подкатегория не связана с выбранной категорией.')
        return cleaned


class StatusForm(BootstrapModelForm):
    class Meta:
        model = Status
        fields = ['name', 'is_active']


class CashFlowTypeForm(BootstrapModelForm):
    class Meta:
        model = CashFlowType
        fields = ['name', 'is_active']


class CategoryForm(BootstrapModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].queryset = CashFlowType.objects.filter(is_active=True)


class SubCategoryForm(BootstrapModelForm):
    class Meta:
        model = SubCategory
        fields = ['name', 'category', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True).select_related('type')
