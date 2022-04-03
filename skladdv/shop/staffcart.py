from decimal import Decimal

from django.conf import settings

from .models import Good


class StaffCart:
    """
    Представляет корзину товаров сотрудника склада
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

    def add(self, good, supplier, quantity=1, update_quantity=False):
        """
        Добавляет товар в корзину или обновляет его количество
        :param good: товар(экземпляр класса Good)
        :param supplier: поставщик(экземпляр класса Supplier)
        :param quantity: кол-во товара(тип - int)
        :param update_quantity: указывает,
        требуется ли обновление количества с заданным количеством (True),
        или же новое количество должно быть добавлено к существующему количеству (False)
        :return: none
        """
        good_id = str(good.id)
        purchase_price = good.purchaseprice_set.filter(pk=supplier.id).purchase_price
        if good_id not in self.cart:
            self.cart[good_id] = {'quantity': 0,
                                  'purchase_price': str(purchase_price),
                                  'supplier_id': supplier.id}
        else:
            self.cart[good_id]['purchase_price'] = str(purchase_price)
        if update_quantity:
            self.cart[good_id]['quantity'] = quantity
        else:
            self.cart[good_id]['quantity'] += quantity
        self.save()

    def save(self):
        """Сохраняет корзину для текущей сессии"""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, good_id):
        """
        Удаляет товар из корзины.
        :param good: id товара(тип - int)
        :return: none
        """
        id = str(good_id)
        if id in self.cart.keys():
            del self.cart[id]
            self.save()

    def __iter__(self):
        """Перебирает элементы в корзине и получает продукты из базы данных"""
        good_ids = self.cart.keys()
        goods = Good.objects.filter(id__in=good_ids)
        for good in goods:
            self.cart[str(good.id)]['title'] = good.title
            self.cart[str(good.id)]['artikul'] = good.artikul
            self.cart[str(good.id)]['id'] = good.id
            supplier_id = self.cart[str(good.id)]['supplier_id']
            purchase_price = good.purchaseprice_set.filter(pk=supplier_id).purchase_price
            self.cart[str(good.id)]['purchase_price'] = str(purchase_price)

        for item in self.cart.values():
            item['total_price'] = str(Decimal(item['purchase_price']) * item['quantity'])
            yield item
        self.save()

    def __len__(self):
        """Подсчитывает общее количество товаров в корзине"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_coast(self):
        """Подсчитывает общую стоимость товаров в корзине"""
        good_ids = self.cart.keys()
        goods = Good.objects.filter(id__in=good_ids)
        for good in goods:
            supplier_id = self.cart[str(good.id)]['supplier_id']
            purchase_price = good.purchaseprice_set.filter(pk=supplier_id).purchase_price
            self.cart[str(good.id)]['purchase_price'] = purchase_price
        return sum(Decimal(item['purchase_price']) * item['quantity'] for item in
                   self.cart.values())

    def clear(self):
        """удаляет корзину из сессии"""
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def count_positions(self):
        """подсчитывает количество позиций в корзине"""
        return len(self.cart)
