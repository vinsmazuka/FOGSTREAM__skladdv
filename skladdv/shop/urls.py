from django.urls import path

from . import views

urlpatterns = [
    path('catalog/cart/', views.show_customer_cart, name='cart'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<int:good_id>/', views.detail, name='detail'),
    path('', views.index, name='index')
]
