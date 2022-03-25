from django.urls import path

from . import views

urlpatterns = [
    path('delete/<int:good_id>/', views.remove_good_from_cart, name='delete'),
    path('catalog/cart/', views.show_customer_cart, name='cart'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<int:good_id>/', views.detail, name='detail'),
    path('', views.index, name='index')
]
