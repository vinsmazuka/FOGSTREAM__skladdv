from django.shortcuts import render

from .models import Category


def index(request):
    return render(request,
                  'shop/catalog.html',
                  {'categories': Category.objects.all()}
                  )


def detail(request, good_id):
    context = {'good_id': good_id}
    return render(request, 'shop/detail.html', context)
