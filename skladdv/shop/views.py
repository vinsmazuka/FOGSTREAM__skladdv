from decimal import Decimal

from django.shortcuts import redirect, render, HttpResponse
from django.contrib.auth.models import User

from .forms import CartAddGood
from .models import Category, Good, Order, OrderItems

from .castomcart import CustomerCart


def index(request):
    """показывает главную страницу сайты"""
    return render(request, 'shop/index.html')


def catalog(request):
    """показывает каталог товаров для покупателя"""
    return render(request,
                  'shop/catalog.html',
                  {'categories': Category.objects.all()}
                  )


def detail(request, good_id):
    """
    показывает страницу товара с формой для заказа
    :param good_id: id товара(тип - int)
    """
    good = Good.objects.get(pk=good_id)
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
            context['messages'] = [f'Заказ создан, кол-во заказанного товара: {quantity}',
                                   f'id товара {good_id}',
                                   f'id пользователя {request.user.id}']
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


def remove_good_from_cart(request, good_id):
    """
    Удаляет товар из корзины
    :param good_id: id товара(тип - int)
    """
    cart = CustomerCart(request)
    good = Good.objects.get(pk=good_id)
    cart.remove(good)
    return redirect('/catalog/cart/')


def clean_cart(request):
    """
    Удаляет все товары из корзины
    """
    cart = CustomerCart(request)
    cart.clear()
    return redirect('/catalog/cart/')


def сreate_order(request):
    """сохраняет заказ покупателя в БД"""
    user_cart = CustomerCart(request)
    user = User.objects.get(pk=request.user.id)
    order = Order(
        user=user,
        positions=user_cart.count_positions(),
        total_coast=user_cart.get_total_coast(),
    )
    order.save()
    goods = list(user_cart.cart.values())
    for item in goods:
        good = Good.objects.get(pk=item['id'])
        order_item = OrderItems(
            order=order,
            good=good,
            position_price=Decimal(item['total_price']),
            position_quantity=item['quantity']
        )
        order_item.save()
    user_cart.clear()
    return HttpResponse(f'Заказ оформлен.Номер заказа: {order.id}')





