import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ValidationError

from catalog.models import MenuItem, StockMovement, Category
from .models import Order, OrderItem
from payments.models import Payment, PaymentMethod

from django.apps import apps
from django.db.models import Q
from django.urls import reverse

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def pos_create_order(request):
    """
    Buat order baru lalu arahkan ke halaman tambah item.
    """
    order_no = uuid.uuid4().hex[:10].upper()
    order = Order.objects.create(user=request.user, order_no=order_no)
    return redirect('pos_add_item', order_no=order.order_no)


@login_required
def pos_add_item(request, order_no):
    order = get_object_or_404(Order, order_no=order_no)

    # FILTER & SEARCH
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('cat', '').strip()

    menu = MenuItem.objects.filter(is_active=True)
    if cat:
        menu = menu.filter(category_id=cat)
    if q:
        menu = menu.filter(Q(name__icontains=q) | Q(category__name__icontains=q))
    menu = menu.select_related('category').order_by('category__name', 'name')

    categories = Category.objects.order_by('name')

    if request.method == 'POST':
        item_id = request.POST.get('menu_item_id')
        try:
            qty = int(request.POST.get('qty', 1))
        except ValueError:
            qty = 1
        if qty < 1:
            qty = 1

        item = get_object_or_404(MenuItem, pk=item_id)

        # ==== VALIDASI STOK (nonaktifkan blok ini jika mau bebas tambah tanpa stok)
        if item.stock_qty <= 0:
            messages.error(request, f"Stok {item.name} habis.")
            return redirect('pos_add_item', order_no=order_no)
        if qty > item.stock_qty:
            messages.warning(request, f"Qty melebihi stok. Maksimum {item.stock_qty}.")
            qty = item.stock_qty
        # ==== akhir validasi stok

        # Tambah / merge item (kalau mau merge qty, pakai get_or_create; di sini create baris baru)
        OrderItem.objects.create(order=order, menu_item=item, qty=qty, price=item.price)
        order.recalc_totals()
        messages.success(request, f"Tambah {item.name} × {qty}")
        # Kembalikan ke halaman yang sama + pertahankan filter
        return redirect(f"{reverse('pos_add_item', args=[order_no])}?q={q}&cat={cat}")

    return render(
        request,
        'pos/add_item.html',
        {'order': order, 'menu': menu, 'categories': categories, 'q': q, 'cat': cat}
    )


def _ensure_payment_methods():
    """
    Buat metode pembayaran default jika tabel masih kosong.
    """
    if not PaymentMethod.objects.exists():
        PaymentMethod.objects.bulk_create([
            PaymentMethod(code="CASH", name="Cash"),
            PaymentMethod(code="CARD", name="Kartu"),
            PaymentMethod(code="QRIS", name="QRIS"),
        ])


@login_required
def pos_checkout(request, order_no):
    order = get_object_or_404(Order, order_no=order_no)

    # Pastikan pilihan metode selalu ada
    _ensure_payment_methods()
    methods = PaymentMethod.objects.all()

    if request.method == 'POST':
        method_id = request.POST.get('payment_method_id')
        ref_no = request.POST.get('ref_no', '').strip()
        card_last4 = request.POST.get('card_last4', '').strip()

        if not method_id:
            messages.error(request, "Pilih metode pembayaran terlebih dahulu.")
            return render(request, 'pos/checkout.html', {'order': order, 'methods': methods})

        pm = get_object_or_404(PaymentMethod, pk=method_id)

        try:
            with transaction.atomic():
                # Buat payment (validasi logic khusus per metode ada di model Payment)
                payment = Payment(
                    order=order,
                    payment_method=pm,
                    amount_paid=order.grand_total,
                    ref_no=ref_no or None,
                    card_last4=card_last4 or None
                )
                payment.full_clean()   # supaya bisa tangkap ValidationError lebih rapi
                payment.save()

                # Finalisasi order & mutasi stok
                order.placed_at = timezone.now()
                order.status = Order.STATUS_PAID
                order.save(update_fields=['placed_at', 'status'])

                for oi in order.items.select_related('menu_item'):
                    oi.menu_item.stock_qty -= oi.qty
                    oi.menu_item.save(update_fields=['stock_qty'])
                    StockMovement.objects.create(
                        menu_item=oi.menu_item,
                        user=request.user,
                        move_type=StockMovement.MOVE_OUT,
                        qty=oi.qty,
                        note=f'Sale {order.order_no}'
                    )

        except ValidationError as ve:
            # Tampilkan error per field dari Payment model (mis. wajib ref_no/card_last4 untuk CARD)
            for field, errs in ve.message_dict.items():
                for msg in errs:
                    messages.error(request, f"{field}: {msg}")
            return render(request, 'pos/checkout.html', {'order': order, 'methods': methods})

        messages.success(request, "Pembayaran berhasil.")
        return redirect('order_receipt', order_no=order_no)

    return render(request, 'pos/checkout.html', {'order': order, 'methods': methods})


@login_required
def order_receipt(request, order_no):
    """
    Halaman struk untuk dicetak. Hanya staff/kasir yang boleh.
    """
    if not request.user.is_staff:
        return redirect('dashboard')

    order = get_object_or_404(
        Order.objects.select_related('customer', 'user').prefetch_related('items__menu_item'),
        order_no=order_no
    )
    shop = {
        "name": "Dapur Bunda Bahagia",
        "address": "Jl. Contoh No. 123, Jakarta",
        "phone": "0812-0000-0000",
    }
    return render(request, "orders/receipt.html", {"order": order, "shop": shop})


# ================== Ambil model Menu tanpa circular import ==================
def get_menu_model():
    for name in ["Menu", "MenuItem", "Product", "Item", "Food"]:
        try:
            return apps.get_model("catalog", name)
        except LookupError:
            continue
    raise LookupError(
        "Model menu tidak ditemukan di app 'catalog'. "
        "Pastikan ada model bernama salah satu dari: Menu, MenuItem, Product, Item, Food"
    )

# ================== Util keranjang berbasis session ==================
def _get_cart(request):
    return request.session.get("cart", {})

def _save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True

# ================== Views Keranjang (untuk halaman publik, terpisah dari POS) ==================
def cart_add(request, menu_id):
    MenuModel = get_menu_model()
    get_object_or_404(MenuModel, id=menu_id)

    cart = _get_cart(request)
    key = str(menu_id)
    cart[key] = cart.get(key, 0) + 1
    _save_cart(request, cart)

    return redirect("catalog:public_menu")

def cart_remove(request, menu_id):
    cart = _get_cart(request)
    key = str(menu_id)
    if key in cart:
        cart[key] -= 1
        if cart[key] <= 0:
            cart.pop(key)
        _save_cart(request, cart)
    return redirect("cart_view")

def cart_clear(request):
    _save_cart(request, {})
    return redirect("cart_view")

def cart_view(request):
    MenuModel = get_menu_model()
    cart = _get_cart(request)

    ids = [int(i) for i in cart.keys()]
    items, total = [], 0

    if ids:
        menus = {m.id: m for m in MenuModel.objects.filter(id__in=ids)}
        for sid, qty in cart.items():
            mid = int(sid)
            m = menus.get(mid)
            if not m:
                continue
            price = getattr(m, "price", 0) or 0
            name = getattr(m, "name", str(m))
            subtotal = price * qty
            total += subtotal
            items.append({
                "id": mid,
                "name": name,
                "price": price,
                "qty": qty,
                "subtotal": subtotal,
            })

    return render(request, "public/cart.html", {"items": items, "total": total})
