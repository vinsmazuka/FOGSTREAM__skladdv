from django.shortcuts import render

from .forms import CartAddGood
from .models import Category, Good

from .castomcart import CustomerCart


def index(request):
    return render(request, 'shop/index.html')


def catalog(request):
    return render(request,
                  'shop/catalog.html',
                  {'categories': Category.objects.all()}
                  )


def detail(request, good_id):
    good = Good.objects.get(pk=good_id)
    good.price = good.price/100
    context = {'good': good}

    def post_response():
        """формирует ответ в случае поступления POST-запроса"""
        form = CartAddGood(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data.get("quantity")
            cart = CustomerCart(request)
            good = Good.objects.get(pk=good_id)
            cart.add(good=good, quantity=quantity)
            print(dict(request.session))
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
