from django.urls import path

from . import views

urlpatterns = [
    path('delete/<int:good_id>/', views.remove_good_from_cart, name='delete'),
    path('makeorder/', views.сreate_order, name='makeorder'),
    path('catalog/cart/', views.show_customer_cart, name='cart'),
    path('catalog/<int:good_id>/', views.detail, name='detail'),
    path('catalog/', views.catalog, name='catalog'),
    path('delete/', views.clean_cart, name='clean'),
    path('', views.index, name='index')
]
