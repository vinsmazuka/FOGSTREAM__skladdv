from django.forms import CharField, IntegerField, Form


class CartAddGood(Form):
    """
    форма для добавления товара в корзину
    """
    quantity = IntegerField()
    quantity.widget.attrs.update(size='15')
    quantity.widget.attrs.update(placeholder='кол-во(целое число)')

