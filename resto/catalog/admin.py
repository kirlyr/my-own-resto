from django.contrib import admin
from .models import Category, MenuItem, StockMovement

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name','code','created_at')
    search_fields = ('name','code')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('id','name','category','price','stock_qty','is_active')
    list_filter = ('category','is_active')
    search_fields = ('name',)

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('id','menu_item','move_type','qty','created_at','user')
    list_filter = ('move_type',)
    search_fields = ('menu_item__name',)