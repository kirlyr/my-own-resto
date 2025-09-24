from django.contrib import admin
from .models import PaymentMethod, Payment


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('id','code','name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id','order','payment_method','amount_paid','paid_at')
    list_filter = ('payment_method',)