from django.forms import ChoiceField, Form, ModelForm, IntegerField


class CartAddGood(Form):
    """
    форма для добавления товара в корзину
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



