from django.contrib import admin

from .models import (
    Category,
    FilterRule,
    ImportHistory,
    PredictionResult,
    Transaction,
    TransactionCategory,
    TransactionMeta,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    list_filter = ['parent']
    search_fields = ['name']


@admin.register(FilterRule)
class FilterRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'art', 'intervall', 'is_active']
    list_filter = ['is_active', 'art', 'intervall']
    search_fields = ['name', 'debitor_contains', 'verwendung_contains']


@admin.register(ImportHistory)
class ImportHistoryAdmin(admin.ModelAdmin):
    list_display = ['filename', 'konto', 'imported_at', 'row_count', 'duplicate_count']
    list_filter = ['imported_at']
    search_fields = ['filename', 'konto']
    readonly_fields = ['file_md5', 'imported_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'debitor', 'value', 'src_konto', 'status']
    list_filter = ['status', 'src_konto']
    search_fields = ['debitor', 'verwendung']
    date_hierarchy = 'date'
    readonly_fields = ['hash', 'imported_at']


@admin.register(TransactionCategory)
class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'category', 'assigned_by', 'assigned_at']
    list_filter = ['assigned_by', 'category']
    search_fields = ['transaction__debitor']


@admin.register(TransactionMeta)
class TransactionMetaAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'rule', 'art', 'prioritaet', 'intervall']
    list_filter = ['art', 'prioritaet', 'intervall']
    search_fields = ['transaction__debitor']


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = ['debitor', 'category', 'next_expected_date', 'avg_interval_days', 'confidence']
    list_filter = ['category']
    search_fields = ['debitor']
