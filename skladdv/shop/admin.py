from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin

from .models import Category, Good


class CategoryAdmin(DjangoMpttAdmin):
    mptt_level_indent = 20


class GoodAdmin(admin.ModelAdmin):
    list_display = ['title', 'available_for_order']
    ordering = ['title']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Good, GoodAdmin)

