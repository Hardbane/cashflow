from typing import Any

from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from rest_framework import filters, viewsets

from .forms import CashFlowRecordForm, CashFlowTypeForm, CategoryForm, StatusForm, SubCategoryForm
from .models import CashFlowRecord, CashFlowType, Category, Status, SubCategory
from .serializers import (
    CashFlowRecordSerializer,
    CashFlowTypeSerializer,
    CategorySerializer,
    StatusSerializer,
    SubCategorySerializer,
)


class CashFlowRecordListView(ListView):
    model = CashFlowRecord
    template_name = 'ledger/record_list.html'
    context_object_name = 'records'
    paginate_by = 25

    def get_queryset(self):
        queryset = (
            CashFlowRecord.objects.select_related('status', 'type', 'category', 'subcategory')
            .all()
        )
        params = self.request.GET
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        status = params.get('status')
        type_id = params.get('type')
        category = params.get('category')
        subcategory = params.get('subcategory')

        if date_from:
            queryset = queryset.filter(record_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(record_date__lte=date_to)
        if status:
            queryset = queryset.filter(status_id=status)
        if type_id:
            queryset = queryset.filter(type_id=type_id)
        if category:
            queryset = queryset.filter(category_id=category)
        if subcategory:
            queryset = queryset.filter(subcategory_id=subcategory)
        return queryset

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context.update(
            statuses=Status.objects.filter(is_active=True),
            types=CashFlowType.objects.filter(is_active=True),
            categories=Category.objects.filter(is_active=True).select_related('type'),
            subcategories=SubCategory.objects.filter(is_active=True).select_related('category'),
            filters=self.request.GET,
        )
        return context


class CashFlowRecordCreateView(CreateView):
    model = CashFlowRecord
    form_class = CashFlowRecordForm
    template_name = 'ledger/record_form.html'
    success_url = reverse_lazy('ledger:record_list')

    def form_valid(self, form):
        messages.success(self.request, 'Запись ДДС создана.')
        return super().form_valid(form)


class CashFlowRecordUpdateView(UpdateView):
    model = CashFlowRecord
    form_class = CashFlowRecordForm
    template_name = 'ledger/record_form.html'
    success_url = reverse_lazy('ledger:record_list')

    def form_valid(self, form):
        messages.success(self.request, 'Запись ДДС обновлена.')
        return super().form_valid(form)


class CashFlowRecordDeleteView(DeleteView):
    model = CashFlowRecord
    template_name = 'ledger/confirm_delete.html'
    success_url = reverse_lazy('ledger:record_list')

    def form_valid(self, form):
        messages.success(self.request, 'Запись ДДС удалена.')
        return super().form_valid(form)


DICTIONARY_CONFIG = {
    'statuses': {
        'model': Status,
        'form': StatusForm,
        'title': 'Статусы',
        'singular': 'статус',
        'columns': ['Название', 'Активно'],
    },
    'types': {
        'model': CashFlowType,
        'form': CashFlowTypeForm,
        'title': 'Типы операций',
        'singular': 'тип операции',
        'columns': ['Название', 'Активно'],
    },
    'categories': {
        'model': Category,
        'form': CategoryForm,
        'title': 'Категории',
        'singular': 'категорию',
        'columns': ['Название', 'Тип', 'Активно'],
    },
    'subcategories': {
        'model': SubCategory,
        'form': SubCategoryForm,
        'title': 'Подкатегории',
        'singular': 'подкатегорию',
        'columns': ['Название', 'Категория', 'Тип', 'Активно'],
    },
}


def dictionaries_view(request):
    context = {'sections': []}
    for slug, config in DICTIONARY_CONFIG.items():
        context['sections'].append(
            {
                'slug': slug,
                'title': config['title'],
                'objects': config['model'].objects.select_related(
                    *(['type'] if slug == 'categories' else ['category', 'category__type'] if slug == 'subcategories' else [])
                ).all(),
            }
        )
    return render(request, 'ledger/dictionaries.html', context)


def get_dictionary_config(kind: str):
    if kind not in DICTIONARY_CONFIG:
        raise Http404('Неизвестный справочник')
    return DICTIONARY_CONFIG[kind]


def dictionary_create(request, kind: str):
    config = get_dictionary_config(kind)
    form_class = config['form']
    form = form_class(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Справочник «{config["title"]}» обновлён.')
        return redirect('ledger:dictionaries')
    return render(
        request,
        'ledger/dictionary_form.html',
        {'form': form, 'title': f'Добавить {config["singular"]}', 'back_url': reverse('ledger:dictionaries')},
    )


def dictionary_update(request, kind: str, pk: int):
    config = get_dictionary_config(kind)
    obj = get_object_or_404(config['model'], pk=pk)
    form = config['form'](request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Справочник «{config["title"]}» обновлён.')
        return redirect('ledger:dictionaries')
    return render(
        request,
        'ledger/dictionary_form.html',
        {'form': form, 'title': f'Редактировать {config["singular"]}', 'back_url': reverse('ledger:dictionaries')},
    )


def dictionary_delete(request, kind: str, pk: int):
    config = get_dictionary_config(kind)
    obj = get_object_or_404(config['model'], pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Элемент справочника удалён.')
        except ProtectedError:
            messages.error(request, 'Нельзя удалить элемент: он используется в записях или зависимых справочниках.')
        return redirect('ledger:dictionaries')
    return render(
        request,
        'ledger/confirm_delete.html',
        {'object': obj, 'cancel_url': reverse('ledger:dictionaries'), 'is_dictionary': True},
    )


def categories_json(request):
    type_id = request.GET.get('type_id')
    categories = Category.objects.filter(is_active=True)
    if type_id:
        categories = categories.filter(type_id=type_id)
    data = [{'id': obj.id, 'name': obj.name} for obj in categories.order_by('name')]
    return JsonResponse({'results': data})


def subcategories_json(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(is_active=True)
    if category_id:
        subcategories = subcategories.filter(category_id=category_id)
    data = [{'id': obj.id, 'name': obj.name} for obj in subcategories.order_by('name')]
    return JsonResponse({'results': data})


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class CashFlowTypeViewSet(viewsets.ModelViewSet):
    queryset = CashFlowType.objects.all()
    serializer_class = CashFlowTypeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related('type').all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'type__name']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        type_id = self.request.query_params.get('type')
        if type_id:
            queryset = queryset.filter(type_id=type_id)
        return queryset


class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.select_related('category', 'category__type').all()
    serializer_class = SubCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'category__name', 'category__type__name']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class CashFlowRecordViewSet(viewsets.ModelViewSet):
    queryset = CashFlowRecord.objects.select_related('status', 'type', 'category', 'subcategory').all()
    serializer_class = CashFlowRecordSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['comment', 'status__name', 'type__name', 'category__name', 'subcategory__name']
    ordering_fields = ['record_date', 'amount', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        filters_map = {
            'status': 'status_id',
            'type': 'type_id',
            'category': 'category_id',
            'subcategory': 'subcategory_id',
        }
        for query_param, field_name in filters_map.items():
            value = params.get(query_param)
            if value:
                queryset = queryset.filter(**{field_name: value})
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        if date_from:
            queryset = queryset.filter(record_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(record_date__lte=date_to)
        return queryset
