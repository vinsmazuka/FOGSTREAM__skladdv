from django.shortcuts import render


def index(request):
    return render(request, 'shop/catalog.html')


def detail(request, good_id):
    context = {'good_id': good_id}
    return render(request, 'shop/detail.html', context)
