import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from catalog.models import MenuItem, StockMovement
from .models import Order, OrderItem
from payments.models import Payment, PaymentMethod

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def pos_create_order(request):
    order_no = uuid.uuid4().hex[:10].upper()
    order = Order.objects.create(user=request.user, order_no=order_no)
    return redirect('pos_add_item', order_no=order_no)

@login_required
def pos_add_item(request, order_no):
    order = get_object_or_404(Order, order_no=order_no)
    menu = MenuItem.objects.filter(is_active=True).order_by('category__name','name')

    if request.method == 'POST':
        item_id = request.POST.get('menu_item_id')
        qty = int(request.POST.get('qty', 1))
        item = get_object_or_404(MenuItem, pk=item_id)
        OrderItem.objects.create(order=order, menu_item=item, qty=qty, price=item.price)
        order.recalc_totals()
        return redirect('pos_add_item', order_no=order_no)

    return render(request, 'pos/add_item.html', {'order': order, 'menu': menu})

@login_required
def pos_checkout(request, order_no):
    order = get_object_or_404(Order, order_no=order_no)
    methods = PaymentMethod.objects.all()

    if request.method == 'POST':
        method_id = request.POST.get('payment_method_id')
        ref_no = request.POST.get('ref_no','')
        card_last4 = request.POST.get('card_last4','')

        with transaction.atomic():
            # Finalisasi order
            order.placed_at = timezone.now()
            order.status = Order.STATUS_PAID
            order.save(update_fields=['placed_at','status'])

            # Buat payment
            pm = get_object_or_404(PaymentMethod, pk=method_id)
            Payment.objects.create(
                order=order, payment_method=pm, amount_paid=order.grand_total,
                ref_no=ref_no, card_last4=card_last4
            )

            # Mutasi stok OUT per item
            for oi in order.items.select_related('menu_item'):
                oi.menu_item.stock_qty -= oi.qty
                oi.menu_item.save(update_fields=['stock_qty'])
                StockMovement.objects.create(
                    menu_item=oi.menu_item, user=request.user, move_type=StockMovement.MOVE_OUT,
                    qty=oi.qty, note=f'Sale {order.order_no}'
                )
        return redirect('dashboard')

    return render(request, 'pos/checkout.html', {'order': order, 'methods': methods})