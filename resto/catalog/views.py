from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .models import Category, MenuItem, StockMovement
from .forms import CategoryForm, MenuItemForm
from django.db.models import Q

staff_required = user_passes_test(lambda u: u.is_staff)

# ---------- CATEGORY ----------
@login_required
@staff_required
def category_list(request):
    q = request.GET.get("q", "")
    sort = request.GET.get("sort", "name")      # name | code | -name | -code
    qs = Category.objects.all()
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)

    allowed = {"name","code","-name","-code"}
    if sort not in allowed:
        sort = "name"
    qs = qs.order_by(sort)

    paginator = Paginator(qs, 10)
    page = request.GET.get("page")
    categories = paginator.get_page(page)
    return render(request, "catalog/category_list.html", {"categories": categories, "q": q, "sort": sort})

@login_required
@staff_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Kategori berhasil ditambahkan.")
        return redirect("category_list")
    return render(request, "catalog/category_form.html", {"form": form, "title": "Tambah Kategori"})

@login_required
@staff_required
def category_update(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Kategori berhasil diperbarui.")
        return redirect("category_list")
    return render(request, "catalog/category_form.html", {"form": form, "title": "Edit Kategori"})

@login_required
@staff_required
def category_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Kategori dihapus.")
        return redirect("category_list")
    return render(request, "catalog/confirm_delete.html", {"object": obj, "back_url": "category_list"})

# ---------- MENU ----------
@login_required
@staff_required
def menu_list(request):
    q = request.GET.get("q", "")
    sort = request.GET.get("sort", "name")  # name | price | stock_qty | -price | -stock_qty
    qs = MenuItem.objects.select_related("category")
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(category__name__icontains=q)

    allowed = {"name","price","stock_qty","-name","-price","-stock_qty"}
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
        return redirect("menu_list")
    return render(request, "catalog/menu_form.html", {"form": form, "title": "Tambah Menu"})

@login_required
@staff_required
def menu_update(request, pk):
    obj = get_object_or_404(MenuItem, pk=pk)
    form = MenuItemForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Menu diperbarui.")
        return redirect("menu_list")
    return render(request, "catalog/menu_form.html", {"form": form, "title": "Edit Menu"})

@login_required
@staff_required
def menu_delete(request, pk):
    obj = get_object_or_404(MenuItem, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Menu dihapus.")
        return redirect("menu_list")
    return render(request, "catalog/confirm_delete.html", {"object": obj, "back_url": "menu_list"})

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
            return redirect("menu_list")

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
        return redirect("menu_list")

    return render(request, "catalog/restock_form.html", {"item": item})

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