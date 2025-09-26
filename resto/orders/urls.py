from django.urls import path
from orders import views as v

urlpatterns = [
    # Dashboard
    path('', v.dashboard, name='dashboard'),

    # POS
    path('pos/create/', v.pos_create_order, name='pos_create_order'),
    path('pos/<str:order_no>/add-item/', v.pos_add_item, name='pos_add_item'),
    path('pos/<str:order_no>/checkout/', v.pos_checkout, name='pos_checkout'),

    # Keranjang
    path('cart/', v.cart_view, name='cart_view'),
    path('cart/add/<int:menu_id>/', v.cart_add, name='cart_add'),
    path('cart/remove/<int:menu_id>/', v.cart_remove, name='cart_remove'),
    path('cart/clear/', v.cart_clear, name='cart_clear'),

    # Receipt
    path('orders/<str:order_no>/receipt/', v.order_receipt, name='order_receipt'),
]
