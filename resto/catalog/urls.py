from django.urls import path
from . import views

urlpatterns = [
    # Category
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_update"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),

    # Menu Items
    path("menu/", views.menu_list, name="menu_list"),
    path("menu/add/", views.menu_create, name="menu_create"),
    path("menu/<int:pk>/edit/", views.menu_update, name="menu_update"),
    path("menu/<int:pk>/delete/", views.menu_delete, name="menu_delete"),
]