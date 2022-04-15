import qrcode
from decimal import Decimal
from email.mime.image import MIMEImage
from smtplib import SMTPDataError

from django.core.mail import EmailMessage
from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User

from .filters import OrderFilter
from .forms import CartAddGood, OrderChangeStatus, StaffCartAddGood
from .models import Category, Good, Order, OrderItems, PurchasePrice, Reserve, Supplier, Supply, SupplyItems

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
    Удаляет все товары из корзины покупателя
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
                reserve_quantity = (good.storage_quantity if item['quantity'] >=
                                    good.storage_quantity else item['quantity'])
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

    order = Order.objects.get(pk=order_id)
    order_current_status = order.status

    def load_info():
        """
        подгружает актуальную информацию о заказе
        """
        order_items = OrderItems.objects.filter(order_id=order_id)
        return order_items

    def post_response():
        """формирует ответ в случае поступления POST-запроса"""
        def send_mail():
            """отправляет письмо о готовности заказа на электронную
            почту покупателя"""
            order.status = new_status
            order.save()
            context['message'] = f'статус заказа изменен на "{new_status}"'
            customer = User.objects.get(pk=order.user_id)
            email_address = customer.email
            data = f'http://127.0.0.1:8000/orders/{order_id}/'
            img = qrcode.make(data)
            file = f'qrcodes/qrcode_order{order_id}.png'
            img.save(file)
            with open(file, 'rb') as f:
                data = MIMEImage(f.read(), "png")
            email = EmailMessage(
                subject=f'qr-код к заказу № {order_id}',
                body='Ваш заказ собран, во вложении qr-код для получения заказа',
                to=[email_address]
            )
            email.attach(data)
            try:
                email.send()
            except SMTPDataError:
                pass

        def close_order():
            """закрывает заказ"""
            reserves = order.reserve_set.all()
            order.status = new_status
            order.save()
            for reserve in reserves:
                good = Good.objects.get(pk=reserve.good_id)
                order_item = OrderItems.objects.get(pk=reserve.order_item_id)
                if reserve.is_actual:
                    reserve.is_actual = False
                    reserve.save()
                    if new_status == 'исполнен':
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
                context['message'] = f'статус заказа изменен на "{new_status}"'

        def do_nothing():
            """
            оставляет заказ без изменения
            """
            context['message'] = 'статус заказа не был изменен'
            pass

        def only_change_status():
            """
            только сохраняет новый статуc заказа
            """
            order.status = new_status
            order.save()
            context['message'] = f'статус заказа изменен на "{new_status}"'

        what_to_do = {
            'создан': {
                'создан': do_nothing,
                'заказан': only_change_status,
                'собран': send_mail,
                'исполнен': do_nothing,
                'отменен': close_order
            },
            'заказан': {
                'создан': do_nothing,
                'заказан': do_nothing,
                'собран': send_mail,
                'исполнен': do_nothing,
                'отменен': close_order
            },
            'собран': {
                'создан': do_nothing,
                'заказан': do_nothing,
                'собран': do_nothing,
                'исполнен': close_order,
                'отменен': close_order
            },
            'исполнен': {
                'создан': do_nothing,
                'заказан': do_nothing,
                'собран': do_nothing,
                'исполнен': do_nothing,
                'отменен': do_nothing
            },
            'отменен': {
                'создан': do_nothing,
                'заказан': do_nothing,
                'собран': do_nothing,
                'исполнен': do_nothing,
                'отменен': do_nothing
            }
        }

        form = OrderChangeStatus(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data.get("status")
            try:
                order.reserve_set.all()
            except Reserve.DoesNotExist:
                pass
            else:
                what_to_do[order_current_status][new_status]()

    def get_response():
        """формирует ответ в случае поступления GET-запроса"""
        pass

    context = {
        'order_id': order.id,
        'user_is_staff': request.user.groups.filter(name='Персонал').exists(),
        'user_is_customer': request.user.groups.filter(name='Покупатели').exists(),
        'order_details': load_info(),
        'order_is_ready': True if order.status == 'собран' else False,
        'form': OrderChangeStatus()
    }

    responses = {
        'POST': post_response,
        'GET': get_response
    }

    responses[request.method]()

    context['order_status'] = order.status

    return render(request, 'shop/order.html', context)


@user_is_authenticated
@staff_only
def orders(request):
    """показывает все заказы покупателей"""
    orders = Order.objects.all().order_by('id')
    filter = OrderFilter(request.GET, queryset=orders)
    context = {'orders': filter}
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
    users = User.objects.all()
    for user in users:
        if user.groups.filter(name='Персонал').exists():
            email_address = user.email
            email = EmailMessage(
                subject=f'заказ № {order_id} исполнен',
                body='покупатель подтвердил получение товара',
                to=[email_address]
            )
            try:
                email.send()
            except SMTPDataError:
                pass
    return redirect('/cabinet/')


@user_is_authenticated
@staff_only
def nomenclature(request):
    """показывает номенклатуру товаров для персонала"""
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
            suppliers_ids = (list(map(lambda x: x.id, suppliers)))
            if int(supplier_id) not in suppliers_ids:
                context['messages'].append('Данного поставщика нет в списке поставщиков товара')
                context['form'] = StaffCartAddGood()
            else:
                supplier = Supplier.objects.get(pk=supplier_id)
                try:
                    purchase_prices = supplier.purchaseprice_set.all()
                    purchase_prices.get(good_id=good_id).purchase_price
                except PurchasePrice.DoesNotExist:
                    context['messages'].append(f'Необходимо внести в БД закупочную '
                                               f'цену для поставщика {supplier.name}')
                    context['form'] = StaffCartAddGood()
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
                                reserve_quantity = 0
                                reserves = order.reserve_set.filter(good_id=good)
                                for reserve in reserves:
                                    if reserve.is_actual:
                                        reserve_quantity += reserve.quantity
                                try:
                                    order_item = order.orderitems_set.get(good_id=good.id)
                                except OrderItems.DoesNotExist:
                                    context['messages'].append('Данного товара нет в заказе')
                                else:
                                    supply_items = order.supplyitems_set.filter(good_id=good.id)
                                    ordered_quantity = 0
                                    for supply_item in supply_items:
                                        if supply_item.status == 'заказана':
                                            ordered_quantity += supply_item.quantity
                                    limit_for_order = order_item.position_quantity\
                                                         - reserve_quantity - ordered_quantity
                                    if quantity > limit_for_order:
                                        context['messages'].append('Вы пытаетесь заказать больше, '
                                                                   'чем нужно для данного заказа')
                                    else:
                                        cart.add(good=good, supplier=supplier, quantity=quantity, order=order)
                                        context['messages'].append('позиция добавлена в Поставку')
                    else:
                        cart.add(good=good, supplier=supplier, quantity=quantity, order='')
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


@user_is_authenticated
@staff_only
def show_staff_cart(request):
    """показывает персоналу содержание его корзины"""
    cart = StaffCart(request)
    total_quantity = len(cart)
    total_cost = cart.get_total_coast()
    context = {
        'cart': cart,
        'total_quantity': total_quantity,
        'total_cost': total_cost
    }
    return render(request, 'shop/staff_cart.html', context)


@user_is_authenticated
@staff_only
def clean_staff_cart(request):
    """
    Удаляет все товары из корзины персонала
    """
    cart = StaffCart(request)
    cart.clear()
    return redirect('/nomenclature/staffcart/')


@user_is_authenticated
@staff_only
def delete_good_staff_cart(request, good_id, supplier_id):
    """
    Удаляет позицию из корзины персонала
    :param good_id: id товара(тип - int)
    :param supplier_id: id поставщика(тип - int)
    """
    cart = StaffCart(request)
    cart.remove(good_id, supplier_id)
    return redirect('/nomenclature/staffcart/')


@user_is_authenticated
@staff_only
def сreate_supply(request):
    """сохраняет поставку в БД"""
    staff_cart = StaffCart(request)
    total_purchase_price = Decimal(0)
    if staff_cart:
        goods = staff_cart.cart
        order_ids = []
        try:
            for good_id, suppliers in goods.items():
                Good.objects.get(pk=int(good_id))
                for supplier_id, value in suppliers.items():
                    supplier = Supplier.objects.get(pk=int(supplier_id))
                    order_id = 0 if not value['order_id'] else value['order_id']
                    order_ids.append(order_id)
                    if not supplier.is_actual:
                        raise Supplier.DoesNotExist
                    else:
                        total_purchase_price += Decimal(value['total_price'])
        except Good.DoesNotExist:
            message = (f"товар {goods[good_id]['title']}, "
                       f"артикул: {goods[good_id]['artikul']} не существует, "
                       f"товар был удален из корзины")
            staff_cart.remove_good(int(good_id))
        except Supplier.DoesNotExist:
            message = (f"поставщик {goods[good_id][supplier_id]['supplier_name']} не существует или "
                       f"не актуальный, позиция с данным поставщиком "
                       f"была удалена из корзины поставок")
            staff_cart.remove(int(good_id), int(supplier_id))
        else:
            if len(set(order_ids)) > 1:
                message = 'все позиции в корзине должны относиться к одному заказу, ' \
                          'исправьте номера заказов'
            else:
                order_id = list(set(order_ids))[0]
                order = Order.objects.get(pk=order_id)
                supply = Supply(
                    total_positions=staff_cart.count_positions(),
                    total_purchase_price=total_purchase_price,
                    order=order
                )
                supply.save()
                message = f'Поставка № {supply.id} создана'
                for good_id, suppliers in goods.items():
                    for value in suppliers.values():
                        good = Good.objects.get(pk=value['good_id'])
                        supplier = Supplier.objects.get(pk=value['supplier_id'])
                        supply_item = SupplyItems(
                            supply=supply,
                            quantity=value['quantity'],
                            good=good,
                            supplier=supplier,
                            purchase_price=value['purchase_price'],
                            order=order,
                            total_purchase_price=value['total_price']
                        )
                        supply_item.save()
                staff_cart.clear()
    else:
        message = 'В корзине нет товаров'
    context = {
        'message': message
    }

    return render(request, 'shop/create_supply_result.html', context)


@user_is_authenticated
@staff_only
def show_supplies(request):
    """показывает все поставки"""
    supplies = Supply.objects.all().order_by('id')

    context = {
        'supplies': supplies
    }

    return render(request, 'shop/supplies.html', context)


@user_is_authenticated
@staff_only
def show_supply_detail(request, supply_id):
    """
    показывает позиции поставки
    :param supply_id: id поставки(тип - int)
    """
    supply = Supply.objects.get(pk=supply_id)
    supply_items = supply.supplyitems_set.all()
    undelivered_positions = 0
    delivered_positions = 0
    for supply_item in supply_items:
        if supply_item.status == 'заказана':
            undelivered_positions += 1
        if supply_item.status == 'поступила на склад':
            delivered_positions += 1
    if not undelivered_positions and not delivered_positions:
        supply.status = 'отменена'
        supply.save()
    elif not undelivered_positions:
        supply.status = 'поступила на склад'
        supply.save()

    context = {
        'supply_items': supply_items,
        'supply_id': supply_id
    }

    return render(request, 'shop/supply.html', context)


@user_is_authenticated
@staff_only
def close_supply_item(request, supply_item_id):
    """
    :param supply_item_id: id позиции в поставке товара(тип - int)
    """
    supply_item = SupplyItems.objects.get(pk=supply_item_id)

    def change_status():
        """изменяет статус позиции в поставке на 'поступила на склад',
         добавляет поступивший товар в резерв под заказ, если поставка
         создавалась под определенный заказ"""
        supply_item.status = 'поступила на склад'
        good = Good.objects.get(pk=supply_item.good_id)
        if supply_item.order_id:
            order = Order.objects.get(pk=supply_item.order_id)
            if order.status != 'отменен' and order.status != 'исполнен':
                supply_item.save()
                order_item = order.orderitems_set.get(good_id=supply_item.good_id)
                reserve = Reserve(
                    order=order,
                    good=good,
                    quantity=supply_item.quantity,
                    order_item=order_item
                )
                reserve.save()
        else:
            good.storage_quantity += supply_item.quantity
            good.save()

    def do_nothing():
        """не изменяет статус позиции"""
        pass

    supply_item_current_status = {
        'поступила на склад': do_nothing,
        'заказана': change_status,
        'отменена': do_nothing
    }

    supply_item_current_status[supply_item.status]()

    return redirect(f'/supplies/{supply_item.supply_id}/')


@user_is_authenticated
@staff_only
def cancel_supply_item(request, supply_item_id):

    supply_item = SupplyItems.objects.get(pk=supply_item_id)

    def change_status():
        """изменяет статус позиции в поставке на 'отменена'"""
        supply_item.status = 'отменена'
        supply_item.save()

    def do_nothing():
        """не изменяет статус позиции"""
        pass

    supply_item_statuses = {
        'поступила на склад': do_nothing,
        'заказана': change_status,
        'отменена': do_nothing
    }

    supply_item_statuses[supply_item.status]()

    return redirect(f'/supplies/{supply_item.supply_id}/')


def show_qrcode(request, order_id):
    """выводит qr-код заказа на новой вкладке браузера"""
    file = f'qrcodes/qrcode_order{order_id}.png'
    try:
        return FileResponse(open(file, 'rb'), content_type='image/png')
    except FileNotFoundError:
        return HttpResponse('Файл не найден')


def create_reserve(request, order_item_id):
    """резервирует свободный остаток на складе под позицию заказа"""
    item = OrderItems.objects.get(pk=order_item_id)
    order = Order.objects.get(pk=item.order_id)
    good = Good.objects.get(pk=item.good_id)
    for_reserve = item.get_for_reserve_quantity()
    if for_reserve and order.status != 'исполнен' \
            and order.status != 'отменен':
        reserve = Reserve(
            order=order,
            good=good,
            quantity=for_reserve,
            order_item=item
        )
        reserve.save()
        good.storage_quantity -= for_reserve
        good.save()
    return redirect(f'/orders/{order.id}/')

























