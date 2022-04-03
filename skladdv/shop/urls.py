from django.urls import path

from . import views

urlpatterns = [
    path('delete/<int:good_id>/', views.remove_good_from_cart, name='delete'),
    path('makeorder/', views.сreate_order, name='makeorder'),
    path('catalog/cart/', views.show_customer_cart, name='cart'),
    path('catalog/<int:good_id>/', views.good_detail, name='good'),
    path('closeorder/<int:order_id>/', views.close_order, name='close_order'),
    path('order/<int:order_id>/', views.order_detail, name='order'),
    path('catalog/categorydetail/<int:cat_id>/', views.category_detail, name='cat_detail'),
    path('nomenclature/categorydetail/<int:cat_id>/', views.nomenclature_category_detail, name='nom_cat_detail'),
    path('staffcart/delete/<int:good_id>/', views.delete_good_staff_cart, name='delete_good_staff_cart'),
    path('nomenclature/<int:good_id>/', views.nomenclature_good_detail, name='nom_good_detail'),
    path('nomenclature/staffcart/', views.show_staff_cart, name='staff_cart'),
    path('nomenclature/', views.nomenclature, name='nomenclature'),
    path('staffcart/delete/', views.clean_staff_cart, name='clean_staff_cart'),
    path('orders/', views.orders, name='orders'),
    path('catalog/', views.catalog, name='catalog'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('delete/', views.clean_cart, name='clean'),
    path('', views.index, name='index')
]

