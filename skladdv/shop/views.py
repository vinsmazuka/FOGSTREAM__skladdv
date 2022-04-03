from decimal import Decimal

from django.shortcuts import redirect, render, HttpResponse
from django.contrib.auth.models import User

from .forms import CartAddGood, OrderChangeStatus, StaffCartAddGood
from .models import Category, Good, Order, OrderItems, PurchasePrice, Reserve, Supplier

from .castomcart import CustomerCart
from .staffcart import StaffCart
from .decorators import customer_only, staff_only, user_is_authenticated


def index(request):
    """показывает главную страницу сайта"""
    return render(request, 'shop/index.html')


def catalog(request):
    """показывает каталог товаров для покупателя"""
    return render(request,
                  'shop/catalog.html',
                  {'categories': Category.objects.all()}
                  )


def category_detail(request, cat_id):
    """
    показывает все товары из категории(для каталога
    покупателя)
    :param cat_id: id категории(тип - int)
    """
    cat = Category.objects.get(pk=cat_id)
    if cat.is_leaf_node():
        goods = Good.objects.filter(category_id=cat_id)
    else:
        sub_cats = list(Category.objects.filter(parent=cat_id))
        goods = Good.objects.filter(category__in=sub_cats)

    context = {'goods': goods}
    return render(request, 'shop/cat_detail.html', context)


def good_detail(request, good_id):
    """
    показывает страницу товара(для покупателя)
    :param good_id: id товара(тип - int)
    """
    try:
        good = Good.objects.get(pk=good_id)
    except Good.DoesNotExist:
        return redirect('/catalog/')
    good.price = good.price
    context = {'good': good}

    def post_response():
        """формирует ответ в случае поступления POST-запроса"""
        form = CartAddGood(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data.get("quantity")
            cart = CustomerCart(request)
            good = Good.objects.get(pk=good_id)
            cart.add(good=good, quantity=quantity)
            context['message'] = 'товар добавлен в корзину'
            form = CartAddGood()
            context['form'] = form

    def get_response():
        """формирует ответ в случае поступления GET-запроса"""
        form = CartAddGood()
        context['form'] = form

    responses = {
        'POST': post_response,
        'GET': get_response
    }
    responses[request.method]()

    return render(request, 'shop/detail.html', context)


@user_is_authenticated
@customer_only
def show_customer_cart(request):
    """показывает покупателю содержание его корзины"""
    cart = CustomerCart(request)
    total_quantity = len(cart)
    total_cost = cart.get_total_coast()
    context = {
        'cart': cart,
        'total_quantity': total_quantity,
        'total_cost': total_cost
    }
    return render(request, 'shop/customer_cart.html', context)


@user_is_authenticated
@customer_only
def remove_good_from_cart(request, good_id):
    """
    Удаляет товар из корзины
    :param good_id: id товара(тип - int)
    """
    cart = CustomerCart(request)
    cart.remove(good_id)
    return redirect('/catalog/cart/')


@user_is_authenticated
@customer_only
def clean_cart(request):
    """
    Удаляет все товары из корзины
    """
    cart = CustomerCart(request)
    cart.clear()
    return redirect('/catalog/cart/')


@user_is_authenticated
@customer_only
def сreate_order(request):
    """сохраняет заказ покупателя в БД"""
    user_cart = CustomerCart(request)
    if user_cart:
        user = User.objects.get(pk=request.user.id)
        goods = list(user_cart.cart.values())
        try:
            for item in goods:
                Good.objects.get(pk=item['id'])
        except Good.DoesNotExist:
            message = (f"товар {item['title']}, артикул: {item['artikul']} не существует, "
                       f"товар был удален из корзины")
            del user_cart.cart[str(item['id'])]
            user_cart.save()
            return message
        else:
            order = Order(
                user=user,
                positions=user_cart.count_positions(),
                total_coast=sum(Decimal(good['price']) * good['quantity'] for good in goods),
            )
            order.save()
            for item in goods:
                good = Good.objects.get(pk=item['id'])
                order_item = OrderItems(
                    order=order,
                    good=good,
                    position_price=Decimal(item['total_price']),
                    position_quantity=item['quantity']
                )
                order_item.save()
                reserve_quantity = good.storage_quantity if item['quantity'] >= good.storage_quantity else item['quantity']
                good.storage_quantity = good.storage_quantity - reserve_quantity
                good.save()
                reserve = Reserve(order=order, good=good, quantity=reserve_quantity, order_item=order_item)
                if reserve_quantity:
                    reserve.save()
            message = f'Заказ оформлен.Номер заказа: {order.id}'
            user_cart.clear()
    else:
        message = 'В корзине нет товаров'
    context = {
        'message': message
    }
    return render(request, 'shop/create_order_result.html', context)


@user_is_authenticated
def cabinet(request):
    """показывает личный кабинет пользователя"""
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id).order_by('id')
    context = {
        'orders': orders,
        'user_is_customer': request.user.groups.filter(name='Покупатели').exists(),
    }
    return render(request, 'shop/cabinet.html', context)


@user_is_authenticated
def order_detail(request, order_id):
    """показывает страницу заказа"""
    def load_info():
        """
        подгружает актуальную информацию о заказе
        """
        order_items = OrderItems.objects.filter(order_id=order_id)
        order_details = []
        for item in order_items:
            try:
                reserve = Reserve.objects.get(order_item_id=item.id)
            except Reserve.DoesNotExist:
                reserve_quantity = 0
            else:
                reserve_quantity = reserve.quantity if reserve.is_actual else 0
            good = Good.objects.get(pk=item.good_id)
            storage_quantity = good.storage_quantity
            for_order = item.position_quantity - reserve_quantity - storage_quantity
            for_order_quantity = for_order if for_order > 0 else 0
            order_detail = {
                'id': item.good_id,
                'title': good.title,
                'quantity': item.position_quantity,
                'price': item.position_price / item.position_quantity,
                'total_price': item.position_price,
                'unit': Good.objects.get(pk=item.good_id).unit,
                'reserve': reserve_quantity,
                'for_order': for_order_quantity,
                'reserve_id': reserve.id if reserve_quantity else 0,
                'storage_quantity': storage_quantity
            }
            order_details.append(order_detail)
        return order_details

    context = {
        'order_id': order_id,
        'user_is_staff': request.user.groups.filter(name='Персонал').exists(),
        'user_is_customer': request.user.groups.filter(name='Покупатели').exists()
    }

    def post_response():
        """формирует ответ в случае поступления POST-запроса"""
        form = OrderChangeStatus(request.POST)
        if form.is_valid():
            status = form.cleaned_data.get("status")
            order = Order.objects.get(pk=order_id)
            order.status = status
            order.save()
            try:
                reserves = order.reserve_set.all()
            except Reserve.DoesNotExist:
                pass
            else:
                if status == 'исполнен' or status == 'отменен':
                    for reserve in reserves:
                            good = Good.objects.get(pk=reserve.good_id)
                            order_item = OrderItems.objects.get(pk=reserve.order_item_id)
                            if reserve.is_actual:
                                reserve.is_actual = False
                                reserve.save()
                                if status == 'исполнен':
                                    new_storage_quantity = (
                                            good.storage_quantity
                                            + reserve.quantity
                                            - order_item.position_quantity
                                    )
                                    good.storage_quantity = new_storage_quantity if new_storage_quantity > 0 else 0
                                else:
                                    good.storage_quantity = (
                                            good.storage_quantity
                                            + reserve.quantity
                                    )
                            good.save()
            context['message'] = f'статус заказа изменен на "{status}"'
            context['form'] = OrderChangeStatus()
            context['order_is_ready'] = True if order.status == 'собран' else False
            context['order_details'] = load_info()

    def get_response():
        """формирует ответ в случае поступления GET-запроса"""
        context['form'] = OrderChangeStatus()
        order = Order.objects.get(pk=order_id)
        context['order_details'] = load_info()
        context['order_is_ready'] = True if order.status == 'собран' else False

    responses = {
        'POST': post_response,
        'GET': get_response
    }

    responses[request.method]()
    return render(request, 'shop/order.html', context)


@user_is_authenticated
@staff_only
def orders(request):
    """показывает все заказы покупателей"""
    orders = Order.objects.all().order_by('id')
    context = {'orders': orders}
    return render(request, 'shop/orders.html', context)


@user_is_authenticated
@customer_only
def close_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    order.status = 'исполнен'
    order.save()
    try:
        reserves = order.reserve_set.all()
    except Reserve.DoesNotExist:
        pass
    else:
        for reserve in reserves:
            good = Good.objects.get(pk=reserve.good_id)
            order_item = OrderItems.objects.get(pk=reserve.order_item_id)
            if reserve.is_actual:
                reserve.is_actual = False
                reserve.save()
                new_storage_quantity = (
                        good.storage_quantity
                        + reserve.quantity
                        - order_item.position_quantity
                )
                good.storage_quantity = new_storage_quantity if new_storage_quantity > 0 else 0
            good.save()
    return redirect('/cabinet/')


@user_is_authenticated
@staff_only
def nomenclature(request):
    """показывает номенклаиуру товаров для персонала"""
    return render(request,
                  'shop/nomenclature.html',
                  {'categories': Category.objects.all()}
                  )


@user_is_authenticated
@staff_only
def nomenclature_category_detail(request, cat_id):
    """
    показывает все товары из категории(для персонала)
    :param cat_id: id категории(тип - int)
    """
    cat = Category.objects.get(pk=cat_id)
    if cat.is_leaf_node():
        goods = Good.objects.filter(category_id=cat_id)
    else:
        sub_cats = list(Category.objects.filter(parent=cat_id))
        goods = Good.objects.filter(category__in=sub_cats)

    context = {'goods': goods}
    return render(request, 'shop/nomenclature_cat_detail.html', context)


@user_is_authenticated
@staff_only
def nomenclature_good_detail(request, good_id):
    """
    показывает страницу товара(для персонала)
    :param good_id: id товара(тип - int)
    """
    context = dict()
    context['messages'] = []
    try:
        good = Good.objects.get(pk=good_id)
    except Good.DoesNotExist:
        return redirect('/catalog/')
    else:
        suppliers = good.suppliers.filter(is_actual=True)
        suppliers_info = []
        for supplier in suppliers:
            if supplier.is_actual:
                try:
                    purchase_prices = supplier.purchaseprice_set.all()
                    purchase_price = purchase_prices.get(good_id=good_id).purchase_price
                except PurchasePrice.DoesNotExist:
                    context['messages'].append('Нет инофрмации о закупочных ценах на товар, '
                                               'чтобы сделать заказ внесите информацию о закупочных ценах')
                    supplier_info = {'name': supplier.name}
                    suppliers_info.append(supplier_info)
                else:
                    supplier_info = {
                        'name': supplier.name,
                        'purchase_price': purchase_price
                    }
                    suppliers_info.append(supplier_info)

        context['good'] = good
        context['suppliers'] = suppliers_info

    def post_response():
        """формирует ответ в случае поступления POST-запроса"""
        form = StaffCartAddGood(request.POST)
        if form.is_valid():
            quantity = int(form.cleaned_data.get("quantity"))
            supplier_id = int(form.cleaned_data.get("supplier"))
            order_id = form.cleaned_data.get("order")
            suppliers_ids = (list(map(lambda x: x.id, suppliers)))
            if int(supplier_id) not in suppliers_ids:
                context['messages'].append('Данного поставщика нет в списке поставщиков товара')
            else:
                supplier = Supplier.objects.get(pk=supplier_id)
                try:
                    purchase_prices = supplier.purchaseprice_set.all()
                    purchase_prices.get(good_id=good_id).purchase_price
                except PurchasePrice.DoesNotExist:
                    context['messages'].append('Необходимо внести в БД закупочную '
                                               'цену для данного поставщика')
                else:
                    cart = StaffCart(request)
                    order_id = form.cleaned_data.get("order")
                    if order_id:
                        try:
                            order = Order.objects.get(pk=int(order_id))
                        except Order.DoesNotExist:
                            context['messages'].append('Данный заказ не существует')
                        else:
                            if order.status == 'исполнен' or order.status == 'отменен':
                                context['messages'].append('Данный заказ не актуальный, '
                                                           'введите номер актуального заказа')
                            else:
                                cart.add(good=good, supplier=supplier, quantity=quantity, order=order)
                                context['messages'].append('позиция добавлена в Поставку')

                    else:
                        cart.add(good=good, supplier=supplier, quantity=quantity, order=None)
                        context['messages'].append('позиция добавлена в Поставку')

                    context['form'] = StaffCartAddGood()

    def get_response():
        """формирует ответ в случае поступления GET-запроса"""
        form = StaffCartAddGood()
        context['form'] = form

    responses = {
        'POST': post_response,
        'GET': get_response
    }
    responses[request.method]()

    return render(request, 'shop/nomenclature_good_detail.html', context)












