from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # CRUD kategori & menu (staff)
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_update"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),

    path("menu/", views.menu_list, name="menu_list"),
    path("menu/add/", views.menu_create, name="menu_create"),
    path("menu/<int:pk>/edit/", views.menu_update, name="menu_update"),
    path("menu/<int:pk>/delete/", views.menu_delete, name="menu_delete"),
    path("menu/<int:pk>/restock/", views.menu_restock, name="menu_restock"),

    # PUBLIC menu + CART (pelanggan)
    path("public/menu/", views.public_menu, name="public_menu"),
    path("public/cart/", views.cart_view, name="cart_view"),
    path("public/cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("public/cart/update/<int:pk>/", views.cart_update, name="cart_update"),
    path("public/cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("public/cart/checkout/", views.cart_checkout, name="cart_checkout"),
]
