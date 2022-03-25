from django.conf import settings


class CustomerCart:
    """
    Представляет корзину товаров покупателя
    """

    def __init__(self, request):
        """
        Инициализация корзины
        :param request: - запрос от пользователя,
        class 'django.core.handlers.wsgi.WSGIRequest'
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, good, quantity=1, update_quantity=False):
        """
        Добавляет товар в корзину или обновляет его количество
        :param good: товар('экземпляр класса Good)
        :param quantity: кол-во товара(тип - int)
        :param update_quantity: указывает,
        требуется ли обновление количества с заданным количеством (True),
        или же новое количество должно быть добавлено к существующему количеству (False)
        :return: none
        """
        good_id = str(good.id)
        if good_id not in self.cart:
            self.cart[good_id] = {'quantity': 0,
                                  'price': good.price}
        if update_quantity:
            self.cart[good_id]['quantity'] = quantity
        else:
            self.cart[good_id]['quantity'] += quantity
        self.save()

    def save(self):
        """Сохраняет корзину для текущей сессии"""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, good):
        """
        Удаляет товар из корзины.
        """
        good_id = str(good.id)
        if good_id in self.cart:
            del self.cart[good_id]
            self.save()



