from django.forms import Form, IntegerField


class CartAddGood(Form):
    """
    форма для добавления товара в корзину
    """
    quantity = IntegerField(min_value=1)
    quantity.widget.attrs.update(size='15')
    quantity.widget.attrs.update(placeholder='кол-во(целое число)')

