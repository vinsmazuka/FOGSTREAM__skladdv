from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin

from .models import Category, Good, Order, PurchasePrice, Supplier, Supply


class CategoryAdmin(DjangoMpttAdmin):
    mptt_level_indent = 20


class GoodAdmin(admin.ModelAdmin):
    list_display = ['title', 'available_for_order']
    search_fields = ['title']


class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn', 'ogrn', 'is_actual']
    search_fields = ['name', 'inn', 'ogrn']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'status']
    search_fields = ['id']


class SupplyAdmin(admin.ModelAdmin):
    list_display = ['id', 'good_id', 'quantity', 'supplier', 'status']
    search_fields = ['id']


class PurchasePriceAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'good', 'purchase_price']
    search_fields = ['good', 'supplier']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Good, GoodAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Supply, SupplyAdmin)
admin.site.register(PurchasePrice, PurchasePriceAdmin)

