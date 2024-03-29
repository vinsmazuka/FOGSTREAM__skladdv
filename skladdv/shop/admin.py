from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin

from .models import Category, Event, Good, Order, PurchasePrice, Reserve, Supplier, Supply, SupplyItems, Contacts


class CategoryAdmin(DjangoMpttAdmin):
    mptt_level_indent = 20


class GoodAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'storage_quantity', 'available_for_order']
    search_fields = ['title']


class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn', 'ogrn', 'is_actual']
    search_fields = ['name', 'inn', 'ogrn']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'positions', 'total_coast', 'status']
    search_fields = ['id']


class SupplyAdmin(admin.ModelAdmin):
    list_display = [''
                    'id',
                    'total_positions',
                    'total_purchase_price',
                    'time_create',
                    'order',
                    'status'
                    ]
    search_fields = ['id']


class SupplyItemsAdmin(admin.ModelAdmin):
    list_display = [''
                    'good',
                    'quantity',
                    'supply',
                    'supplier',
                    'purchase_price',
                    'status'
                    ]
    search_fields = ['order', 'good']


class PurchasePriceAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'good', 'purchase_price']
    search_fields = ['good', 'supplier']


class ReserveAdmin(admin.ModelAdmin):
    list_display = ['good', 'order', 'quantity', 'is_actual']
    search_fields = ['good', 'order']


class ContactsAdmin(admin.ModelAdmin):
    list_display = ['telephone', 'user']
    search_fields = ['telephone', 'user']


class EventAdmin(admin.ModelAdmin):
    list_display = ['type', 'supplier', 'good', 'customer', 'created_by']
    search_fields = ['type', 'supplier', 'good', 'customer', 'created_by']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Good, GoodAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Supply, SupplyAdmin)
admin.site.register(SupplyItems, SupplyItemsAdmin)
admin.site.register(PurchasePrice, PurchasePriceAdmin)
admin.site.register(Reserve, ReserveAdmin)
admin.site.register(Contacts, ContactsAdmin)
admin.site.register(Event, EventAdmin)
