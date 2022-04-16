import django_filters

from .models import Good, Order, Supplier, Supply


class OrderFilter(django_filters.FilterSet):
    """предназначен для создания фильтров
    объекта qs класса Order
    на страницах сайта"""
    time_create = django_filters.DateFilter(
        input_formats=['%d-%m-%Y'],
        lookup_expr='icontains'
    )
    id = django_filters.NumberFilter(label='№ заказа')

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'user',
            'time_create'
        ]


class SupplyFilter(django_filters.FilterSet):
    """предназначен для создания фильтров
     объекта qs класса Supply
     на страницах сайта"""
    time_create = django_filters.DateFilter(
        input_formats=['%d-%m-%Y'],
        lookup_expr='icontains'
    )
    id = django_filters.NumberFilter(label='№ поставки')
    order_id = django_filters.NumberFilter()

    class Meta:
        model = Supply
        fields = [
            'id',
            'status',
            'time_create',
            'order_id'
        ]


class GoodFilter(django_filters.FilterSet):
    """предназначен для создания фильтров
    объекта qs класса Good
    на страницах сайта"""
    suppliers = django_filters.ModelChoiceFilter(
        queryset=Supplier.objects.all())

    class Meta:
        model = Good
        fields = [
            'title',
            'artikul',
            'suppliers'
        ]

