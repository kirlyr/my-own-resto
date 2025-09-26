from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.public_menu, name='public_menu'),
    path('cart/', v.cart_view, name='public_cart'),
    path('cart/add/<int:item_id>/', v.cart_add, name='public_cart_add'),
    path('cart/remove/<int:item_id>/', v.cart_remove, name='public_cart_remove'),
    path('checkout/', v.cart_checkout, name='public_checkout'),
    # tambahkan kalau ada: success page dll.
]
