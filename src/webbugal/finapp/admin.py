from django.contrib import admin
from .models import EUR
# Register your models here.

class EURAdmin(admin.ModelAdmin):
    list_filter = ['position', 'value', 'category', 'inout']
    list_display = ['position', 'value', 'category', 'inout']
    search_fields = ['position']
    prepopulated_fields = {"slug": ("position",)}

admin.site.register(EUR, EURAdmin)