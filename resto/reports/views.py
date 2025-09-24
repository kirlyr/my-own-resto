from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from orders.models import Order, OrderItem


@login_required
def sales_monthly(request):
    qs = (Order.objects.filter(status='PAID')
    .extra(select={'ym': "DATE_FORMAT(placed_at,'%%Y-%%m')"})
    .values('ym')
    .annotate(revenue=Sum('grand_total'))
    .order_by('-ym'))
    return render(request, 'reports/sales_monthly.html', {'rows': qs})


@login_required
def top_items_weekly(request):
    qs = (OrderItem.objects.filter(order__status='PAID')
    .extra(select={'yw': "YEARWEEK(orders_order.placed_at,1)"})
    .values('yw','menu_item__name')
    .annotate(total_qty=Sum('qty'))
    .order_by('-yw','-total_qty'))
    return render(request, 'reports/top_items_weekly.html', {'rows': qs})