from django.shortcuts import render

from .models import Category, Good


def index(request):
    return render(request,
                  'shop/catalog.html',
                  {'categories': Category.objects.all()}
                  )


def detail(request, good_id):
    good = Good.objects.get(pk= good_id)
    context = {'good': good}
    return render(request, 'shop/detail.html', context)
