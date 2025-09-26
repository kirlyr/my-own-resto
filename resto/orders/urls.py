from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from orders import views as orders_views
# OPSIONAL: aktifkan kalau kamu punya public_menu di catalog
# from catalog import views as catalog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', orders_views.dashboard, name='dashboard'),

    # Public menu (opsional, sesuaikan kalau ada)
    # path('public/menu/', catalog_views.public_menu, name='public_menu'),

    # POS
    path('pos/create/', orders_views.pos_create_order, name='pos_create_order'),
    path('pos/<str:order_no>/add-item/', orders_views.pos_add_item, name='pos_add_item'),
    path('pos/<str:order_no>/checkout/', orders_views.pos_checkout, name='pos_checkout'),

    # === Fix utama NoReverseMatch ===
    # Jadikan 'cart_view' ada. Kita alias ke pos_create_order agar link di template tetap jalan.
    path('cart/', orders_views.pos_create_order, name='cart_view'),

    # Receipt
    path('orders/<str:order_no>/receipt/', orders_views.order_receipt, name='order_receipt'),
]
