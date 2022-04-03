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

    def add(self, good, supplier, order=None, quantity=1, update_quantity=False):
        """
        Добавляет товар в корзину или обновляет его количество
        :param good: товар(экземпляр класса Good)
        :param order: заказ(экземпляр класса Order)
        :param supplier: поставщик(экземпляр класса Supplier)
        :param quantity: кол-во товара(тип - int)
        :param update_quantity: указывает,
        требуется ли обновление количества с заданным количеством (True),
        или же новое количество должно быть добавлено к существующему количеству (False)
        :return: none
        """
        good_id = str(good.id)
        if order:
            order_id = order.id
        else:
            order_id = None
        supplier_id = str(supplier.id)
        purchase_price = good.purchaseprice_set.get(supplier_id=supplier.id).purchase_price
        if good_id not in self.cart:
            self.cart[good_id] = {supplier_id: {'quantity': 0,
                                                'purchase_price': str(purchase_price),
                                                'supplier_name': supplier.name,
                                                'order_id': order_id
                                                }
                                  }
        elif supplier_id not in self.cart[good_id]:
            self.cart[good_id][supplier_id] = {'quantity': 0,
                                               'purchase_price': str(purchase_price),
                                               'supplier_name': supplier.name,
                                               'order_id': order_id
                                               }
        self.cart[good_id][supplier_id]['purchase_price'] = str(purchase_price)
        if update_quantity:
            self.cart[good_id][supplier_id]['quantity'] = quantity
        else:
            self.cart[good_id][supplier_id]['quantity'] += quantity
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
            good_id = str(good.id)
            suppliers = self.cart[good_id]
            for supplier in suppliers:
                supplier_id = supplier
                purchase_price = good.purchaseprice_set.get(supplier_id=supplier_id).purchase_price
                self.cart[good_id][supplier_id]['title'] = good.title
                self.cart[good_id][supplier_id]['artikul'] = good.artikul
                self.cart[good_id][supplier_id]['id'] = good.id
                self.cart[good_id][supplier_id]['purchase_price'] = str(purchase_price)

        for item in self.cart.values():
            for supplier in item.values():
                supplier['total_price'] = str(Decimal(supplier['purchase_price']) * supplier['quantity'])
                yield supplier
        self.save()

    def __len__(self):
        """Подсчитывает общее количество товаров в корзине"""
        count = 0
        for item in self.cart.values():
            for supplier in item.values():
                count += supplier['quantity']
        return count

    def get_total_coast(self):
        """Подсчитывает общую стоимость товаров в корзине"""
        good_ids = self.cart.keys()
        goods = Good.objects.filter(id__in=good_ids)
        total_coast = 0
        for good in goods:
            good_id = str(good.id)
            suppliers = self.cart[good_id]
            for supplier in suppliers:
                supplier_id = supplier
                purchase_price = good.purchaseprice_set.get(supplier_id=int(supplier_id)).purchase_price
                self.cart[good_id][supplier_id]['purchase_price'] = purchase_price
                total_coast += (Decimal(
                    self.cart[good_id][supplier_id]['purchase_price'])
                                * self.cart[good_id][supplier_id]['quantity'])
        return total_coast

    def clear(self):
        """удаляет корзину из сессии"""
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def count_positions(self):
        """подсчитывает количество позиций в корзине"""
        count = 0
        for key, value in self.cart.items():
            count += len(value)
        return count


