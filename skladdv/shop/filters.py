import django_filters

from .models import Order


class OrderFilter(django_filters.FilterSet):
    time_create = django_filters.DateFilter(input_formats=['%d-%m-%Y'], lookup_expr='icontains')
    id = django_filters.NumberFilter(label='номер')

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'user',
            'time_create'
        ]
