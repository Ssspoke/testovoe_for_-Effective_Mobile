from django.urls import path
from .views import list_products, create_product, list_orders, create_order

urlpatterns = [
    path('products/', list_products, name='list_products'),
    path('products/create/', create_product, name='create_product'),
    path('orders/', list_orders, name='list_orders'),
    path('orders/create/', create_order, name='create_order'),
]
