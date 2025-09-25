from django.contrib import admin
from .models import Customer, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','order_no','status','grand_total','placed_at','user','customer')
    list_filter = ('status',)
    search_fields = ('order_no','customer__name')
    inlines = [OrderItemInline]

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id','name','phone','email','created_at')
    search_fields = ('name','phone','email')