from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin

from .models import Category, Good, Order, Supplier, Supply


class CategoryAdmin(DjangoMpttAdmin):
    mptt_level_indent = 20


class GoodAdmin(admin.ModelAdmin):
    list_display = ['title', 'available_for_order']
    search_fields = ['title']


class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_actual']
    search_fields = ['name']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'status']
    search_fields = ['id']


class SupplyAdmin(admin.ModelAdmin):
    list_display = ['id', 'good', 'quantity', 'supplier', 'status', 'time_supply']
    search_fields = ['id']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Good, GoodAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Supply, SupplyAdmin)

