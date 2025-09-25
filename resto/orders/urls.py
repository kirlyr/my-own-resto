from django.contrib import admin
from django.urls import path
from orders.views import dashboard, pos_create_order, pos_add_item, pos_checkout
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', dashboard, name='dashboard'),
    path('pos/create/', pos_create_order, name='pos_create_order'),
    path('pos/<str:order_no>/add-item/', pos_add_item, name='pos_add_item'),
    path('pos/<str:order_no>/checkout/', pos_checkout, name='pos_checkout'),
]