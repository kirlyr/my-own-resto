from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.dashboard, name='pos_dashboard'),
    path('create/', v.pos_create_order, name='pos_create_order'),
    path('<str:order_no>/add-item/', v.pos_add_item, name='pos_add_item'),
    path('<str:order_no>/checkout/', v.pos_checkout, name='pos_checkout'),
    path('<str:order_no>/receipt/', v.order_receipt, name='pos_receipt'),
]
