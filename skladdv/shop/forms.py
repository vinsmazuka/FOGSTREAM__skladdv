from django.forms import CharField, Form


class CartAddGood(Form):
    """
    форма для добавления товара в корзину
    """
    quantity = CharField(max_length=10)
    quantity.widget.attrs.update(size='15')
    quantity.widget.attrs.update(placeholder='Введите количество')

