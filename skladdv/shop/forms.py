from django.forms import ChoiceField, Form, ModelForm, IntegerField

from .models import Supplier


class CartAddGood(Form):
    """
    форма для добавления товара в корзину покупателя
    """
    quantity = IntegerField(min_value=1)
    quantity.widget.attrs.update(size='15')
    quantity.widget.attrs.update(placeholder='кол-во(целое число)')


class OrderChangeStatus(Form):
    """
    форма для изменения статуса заказа
    """
    CHOICES = (
        ('создан', 'создан'),
        ('заказан', 'заказан'),
        ('собран', 'собран'),
        ('исполнен', 'исполнен'),
        ('отменен', 'отменен')
    )
    status = ChoiceField(choices=CHOICES)


class StaffCartAddGood(Form):
    """
    форма для добавления товара в корзину персонала
    """
    quantity = IntegerField(min_value=1)
    quantity.widget.attrs.update(size='15')
    quantity.widget.attrs.update(placeholder='кол-во(целое число)')
    supplier = ChoiceField()
    order = IntegerField(min_value=1)
    order.widget.attrs.update(size='15')
    order.widget.attrs.update(placeholder='№ заказа')

    def __init__(self, *args, **kwargs):
        super(StaffCartAddGood, self).__init__(*args, **kwargs)
        self.fields['supplier'].choices = list((supplier.id, supplier.name) for
                                               supplier in Supplier.objects.filter(is_actual=True))






