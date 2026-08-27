from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('import/', views.ImportView.as_view(), name='import'),
    path('import/history/', views.import_history, name='import_history'),
    path('import/<int:pk>/delete/', views.ImportDeleteView.as_view(), name='import_delete'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/<int:pk>/meta/', views.transaction_meta_save, name='transaction_meta_save'),
    path('transactions/<int:pk>/meta/clear/', views.transaction_meta_clear, name='transaction_meta_clear'),
    path('transactions/<int:pk>/category/<int:cat_pk>/remove/', views.transaction_category_remove, name='transaction_category_remove'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/new/<int:pk>/', views.CategoryNewSubView.as_view(), name='category_new_sub'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('rules/', views.RuleListView.as_view(), name='rule_list'),
    path('rules/<int:pk>/edit/', views.RuleUpdateView.as_view(), name='rule_edit'),
    path('rules/<int:pk>/delete/', views.RuleDeleteView.as_view(), name='rule_delete'),
    path('predictions/', views.prediction_list, name='prediction_list'),
    path('reports/euer/', views.report_euer, name='report_euer'),
]
