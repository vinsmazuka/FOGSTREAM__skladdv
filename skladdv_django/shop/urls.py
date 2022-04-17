from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('staffcart/delete/<int:good_id>/<int:supplier_id>/', views.delete_good_staff_cart, name='delete_good_staff_cart'),
    path('nomenclature/categorydetail/<int:cat_id>/', views.nomenclature_category_detail, name='nom_cat_detail'),
    path('catalog/categorydetail/<int:cat_id>/', views.category_detail, name='cat_detail'),
    path('supplies/closesupplyitem/<int:supply_item_id>/', views.close_supply_item, name='close_supply_item'),
    path('supplies/cancelsupplyitem/<int:supply_item_id>/', views.cancel_supply_item, name='cancel_supply_item'),
    path('suppliers/supplyitems/<int:supplier_id>/', views.supplier_supplyitems, name='supplier_supplyitems'),
    path('customers/orders/<int:user_id>/', views.customer_orders, name='customer_orders'),
    path('nomenclature/<int:good_id>/', views.nomenclature_good_detail, name='nom_good_detail'),
    path('nomenclature/staffcart/', views.show_staff_cart, name='staff_cart'),
    path('staffcart/delete/', views.clean_staff_cart, name='clean_staff_cart'),
    path('catalog/cart/', views.show_customer_cart, name='cart'),
    path('catalog/<int:good_id>/', views.good_detail, name='good'),
    path('closeorder/<int:order_id>/', views.close_order, name='close_order'),
    path('qrcode/<int:order_id>/', views.show_qrcode, name='qrcode'),
    path('orders/<int:order_id>/', views.order_detail, name='order'),
    path('supplies/<int:supply_id>/', views.show_supply_detail, name='supply_detail'),
    path('delete/<int:good_id>/', views.remove_good_from_cart, name='delete'),
    path('reserve/<int:order_item_id>/', views.create_reserve, name='reserve'),
    path('suppliercreate/', views.supplier_create, name='supplier_create'),
    path('customercreate/', views.customer_create, name='customer_create'),
    path('makeorder/', views.сreate_order, name='makeorder'),
    path('createsupply/', views.сreate_supply, name='create_supply'),
    path('nomenclature/', views.nomenclature, name='nomenclature'),
    path('orders/', views.orders, name='orders'),
    path('catalog/', views.catalog, name='catalog'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('delete/', views.clean_cart, name='clean'),
    path('suppliers/', views.suppliers, name='suppliers'),
    path('supplies/', views.show_supplies, name='supplies'),
    path('customers/', views.customers, name='customers'),
    path('operations/', views.operations, name='operations'),
    path('', views.index, name='index')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

