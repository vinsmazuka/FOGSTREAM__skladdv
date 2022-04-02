from decimal import Decimal

from django.shortcuts import redirect, render
from django.contrib.auth.models import User

from .forms import CartAddGood
from .models import Category, Good, Order, OrderItems, Reserve

from .castomcart import CustomerCart
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
    показывает все товары из категории
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
    показывает страницу товара с формой для заказа
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
                reserve = Reserve(order=order, good=good, quantity=reserve_quantity)
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
@customer_only
def cabinet(request):
    """показывает личный кабинет пользователя"""
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id).order_by('id')
    context = {'orders': orders}
    return render(request, 'shop/cabinet.html', context)


@user_is_authenticated
def order_detail(request, order_id):
    """показывает страницу заказа"""
    order_items = OrderItems.objects.filter(order_id=order_id)
    order_details = []
    for item in order_items:
        order_detail = {
            'title': Good.objects.get(pk=item.good_id).title,
            'quantity': item.position_quantity,
            'price': item.position_price/item.position_quantity,
            'total_price': item.position_price,
            'unit': Good.objects.get(pk=item.good_id).unit
        }
        order_details.append(order_detail)

    context = {
        'order_details': order_details,
        'order_id': order_id
    }
    return render(request, 'shop/order.html', context)


@user_is_authenticated
@staff_only
def orders(request):
    """показывает все заказы покупателей"""
    orders = Order.objects.all().order_by('id')
    context = {'orders': orders}
    return render(request, 'shop/orders.html', context)











