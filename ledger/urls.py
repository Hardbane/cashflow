from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'ledger'

router = DefaultRouter()
router.register('statuses', views.StatusViewSet)
router.register('types', views.CashFlowTypeViewSet)
router.register('categories', views.CategoryViewSet)
router.register('subcategories', views.SubCategoryViewSet)
router.register('records', views.CashFlowRecordViewSet)

urlpatterns = [
    path('', views.CashFlowRecordListView.as_view(), name='record_list'),
    path('records/add/', views.CashFlowRecordCreateView.as_view(), name='record_create'),
    path('records/<int:pk>/edit/', views.CashFlowRecordUpdateView.as_view(), name='record_update'),
    path('records/<int:pk>/delete/', views.CashFlowRecordDeleteView.as_view(), name='record_delete'),
    path('dictionaries/', views.dictionaries_view, name='dictionaries'),
    path('dictionaries/<str:kind>/add/', views.dictionary_create, name='dictionary_create'),
    path('dictionaries/<str:kind>/<int:pk>/edit/', views.dictionary_update, name='dictionary_update'),
    path('dictionaries/<str:kind>/<int:pk>/delete/', views.dictionary_delete, name='dictionary_delete'),
    path('ajax/categories/', views.categories_json, name='categories_json'),
    path('ajax/subcategories/', views.subcategories_json, name='subcategories_json'),
    path('api/', include(router.urls)),
]
