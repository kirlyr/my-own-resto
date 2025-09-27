from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .models import Category, MenuItem, StockMovement
from .forms import CategoryForm, MenuItemForm
from django.db.models import Q
from django.urls import reverse
from decimal import Decimal
from orders.models import Order, OrderItem, Customer

staff_required = user_passes_test(lambda u: u.is_staff)

CART_KEY = 'cart'  # session key

# ---------- CATEGORY ----------
@login_required
@staff_required
def category_list(request):
    q = request.GET.get("q", "")
    sort = request.GET.get("sort", "name")      # name | code | -name | -code
    qs = Category.objects.all()
    if q:
        # gabungkan filter nama/kode
        qs = (Category.objects.filter(name__icontains=q) |
              Category.objects.filter(code__icontains=q))

    allowed = {"name", "code", "-name", "-code"}
    if sort not in allowed:
        sort = "name"
    qs = qs.order_by(sort)

    paginator = Paginator(qs, 10)
    page = request.GET.get("page")
    categories = paginator.get_page(page)
    return render(request, "catalog/category_list.html", {
        "categories": categories, "q": q, "sort": sort
    })

@login_required
@staff_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Kategori berhasil ditambahkan.")
        return redirect("catalog:category_list")
    return render(request, "catalog/category_form.html",
                  {"form": form, "title": "Tambah Kategori"})

@login_required
@staff_required
def category_update(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Kategori berhasil diperbarui.")
        return redirect("catalog:category_list")
    return render(request, "catalog/category_form.html",
                  {"form": form, "title": "Edit Kategori"})

@login_required
@staff_required
def category_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Kategori dihapus.")
        return redirect("catalog:category_list")
    # pastikan back_url sudah namespaced
    return render(request, "catalog/confirm_delete.html",
                  {"object": obj, "back_url": "catalog:category_list"})

# ---------- MENU ----------
@login_required
@staff_required
def menu_list(request):
    q = request.GET.get("q", "")
    sort = request.GET.get("sort", "name")  # name | price | stock_qty | -price | -stock_qty
    qs = MenuItem.objects.select_related("category")
    if q:
        qs = (MenuItem.objects.filter(name__icontains=q) |
              MenuItem.objects.filter(category__name__icontains=q))

    allowed = {"name", "price", "stock_qty", "-name", "-price", "-stock_qty"}
    if sort not in allowed:
        sort = "name"
    qs = qs.order_by(sort, "id")

    paginator = Paginator(qs, 10)
    page = request.GET.get("page")
    items = paginator.get_page(page)
    return render(request, "catalog/menu_list.html", {"items": items, "q": q, "sort": sort})

@login_required
@staff_required
def menu_create(request):
    form = MenuItemForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Menu berhasil ditambahkan.")
        return redirect("catalog:menu_list")
    return render(request, "catalog/menu_form.html",
                  {"form": form, "title": "Tambah Menu"})

@login_required
@staff_required
def menu_update(request, pk):
    obj = get_object_or_404(MenuItem, pk=pk)
    form = MenuItemForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Menu diperbarui.")
        return redirect("catalog:menu_list")
    return render(request, "catalog/menu_form.html",
                  {"form": form, "title": "Edit Menu"})

@login_required
@staff_required
def menu_delete(request, pk):
    obj = get_object_or_404(MenuItem, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Menu dihapus.")
        return redirect("catalog:menu_list")
    return render(request, "catalog/confirm_delete.html",
                  {"object": obj, "back_url": "catalog:menu_list"})

@login_required
@staff_required
def menu_restock(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == "POST":
        try:
            qty = int(request.POST.get("qty", "0"))
        except ValueError:
            qty = 0
        if qty <= 0:
            messages.error(request, "Qty restock harus lebih dari 0.")
            return redirect("catalog:menu_list")

        with transaction.atomic():
            item.stock_qty += qty
            item.save(update_fields=["stock_qty"])
            StockMovement.objects.create(
                menu_item=item,
                user=request.user,
                move_type=StockMovement.MOVE_IN,
                qty=qty,
                note="Restock via UI"
            )
        messages.success(request, f"Restock {item.name} +{qty} berhasil.")
        return redirect("catalog:menu_list")

    return render(request, "catalog/restock_form.html", {"item": item})

# ---------- PUBLIC ----------
def public_menu(request):
    """
    Halaman publik untuk customer melihat menu yang tersedia.
    Fitur: search, filter kategori, pagination. Hanya item aktif (is_active=True) dan stock > 0.
    """
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "").strip()
    page = request.GET.get("page")

    categories = Category.objects.order_by("name")
    items = MenuItem.objects.select_related("category").filter(is_active=True, stock_qty__gt=0)

    if cat:
        items = items.filter(category__id=cat)
    if q:
        items = items.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        )

    items = items.order_by("category__name", "name")
    paginator = Paginator(items, 12)
    items_page = paginator.get_page(page)

    return render(request, "public/menu.html", {
        "categories": categories,
        "items": items_page,
        "q": q,
        "cat": cat,
    })

# ========= CART (Session) =========
def _get_cart(session):
    return session.get(CART_KEY, {})

def _save_cart(session, cart):
    session[CART_KEY] = cart
    session.modified = True

def cart_add(request, pk):
    """Tambah 1 item (atau qty dari form) ke keranjang session."""
    try:
        qty = int(request.POST.get('qty', 1))
    except ValueError:
        qty = 1
    if qty < 1:
        qty = 1

    item = get_object_or_404(MenuItem, pk=pk, is_active=True, stock_qty__gt=0)
    cart = _get_cart(request.session)
    current = int(cart.get(str(pk), 0))
    qty = min(qty, item.stock_qty)  # clamp ke stok

    cart[str(pk)] = current + qty
    _save_cart(request.session, cart)
    messages.success(request, f"Tambahkan {item.name} × {qty} ke keranjang.")

    # Kembali ke halaman sebelumnya, fallback ke public_menu (namespaced!)
    return redirect(request.META.get('HTTP_REFERER') or reverse('catalog:public_menu'))

def cart_view(request):
    """Tampilkan isi keranjang + subtotal, pajak, grand total."""
    from decimal import Decimal  # pastikan Decimal tersedia di fungsi ini juga
    cart = _get_cart(request.session)
    if not cart:
        return render(request, 'public/cart.html', {
            'rows': [],
            'subtotal': Decimal('0.00'),
            'tax': Decimal('0.00'),
            'grand': Decimal('0.00'),
        })

    ids = [int(k) for k in cart.keys()]
    items = MenuItem.objects.filter(id__in=ids).select_related('category')

    rows = []
    subtotal = Decimal('0.00')
    for m in items:
        q = int(cart[str(m.id)])
        line = (m.price * q)
        rows.append({'item': m, 'qty': q, 'line': line})
        subtotal += line

    tax = (subtotal * Decimal('0.10')).quantize(Decimal('0.01'))
    grand = (subtotal + tax).quantize(Decimal('0.01'))

    return render(request, 'public/cart.html', {
        'rows': rows, 'subtotal': subtotal, 'tax': tax, 'grand': grand
    })

def cart_update(request, pk):
    """Ubah qty suatu item di keranjang."""
    try:
        qty = int(request.POST.get('qty', 1))
    except ValueError:
        qty = 1
    if qty < 1:
        qty = 1
    item = get_object_or_404(MenuItem, pk=pk, is_active=True)
    qty = min(qty, item.stock_qty)

    cart = _get_cart(request.session)
    if str(pk) in cart:
        cart[str(pk)] = qty
        _save_cart(request.session, cart)
        messages.success(request, "Qty diperbarui.")
    return redirect('catalog:cart_view')

def cart_remove(request, pk):
    """Hapus item dari keranjang."""
    cart = _get_cart(request.session)
    if str(pk) in cart:
        del cart[str(pk)]
        _save_cart(request.session, cart)
        messages.success(request, "Item dihapus dari keranjang.")
    return redirect('catalog:cart_view')

@login_required
def cart_checkout(request):
    """
    Buat Order dari isi keranjang (butuh login staff/kasir).
    Redirect ke halaman checkout POS untuk proses pembayaran.
    """
    cart = _get_cart(request.session)
    if not cart:
        messages.error(request, "Keranjang kosong.")
        return redirect('catalog:public_menu')

    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip() or 'Guest'
        phone = (request.POST.get('phone') or '').strip()
        customer, _ = Customer.objects.get_or_create(name=name, phone=phone)

        import uuid
        order_no = uuid.uuid4().hex[:10].upper()
        o = Order.objects.create(user=request.user, customer=customer, order_no=order_no)

        items = MenuItem.objects.filter(id__in=[int(k) for k in cart.keys()])
        for m in items:
            q = min(int(cart[str(m.id)]), m.stock_qty)
            OrderItem.objects.create(order=o, menu_item=m, qty=q, price=m.price)

        o.recalc_totals()
        _save_cart(request.session, {})  # kosongkan keranjang
        messages.success(request, f"Order {o.order_no} dibuat. Lanjut ke pembayaran.")
        return redirect('pos_checkout', order_no=o.order_no)

    # GET → tampilkan form singkat data pelanggan
    return render(request, 'public/checkout.html')
# ========= END CART =========
