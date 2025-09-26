from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from .models import Category, MenuItem
from .forms import CategoryForm, MenuItemForm

staff_required = user_passes_test(lambda u: u.is_staff)

# ---------- CATEGORY ----------
@login_required
@staff_required
def category_list(request):
    q = request.GET.get("q", "")
    categories = Category.objects.all().order_by("name")
    if q:
        categories = categories.filter(name__icontains=q) | categories.filter(code__icontains=q)
    return render(request, "catalog/category_list.html", {"categories": categories, "q": q})

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
    qs = MenuItem.objects.select_related("category").order_by("category__name", "name")
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(category__name__icontains=q)
    return render(request, "catalog/menu_list.html", {"items": qs, "q": q})

@login_required
@staff_required
def menu_create(request):
    form = MenuItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Menu berhasil ditambahkan.")
        return redirect("menu_list")
    return render(request, "catalog/menu_form.html", {"form": form, "title": "Tambah Menu"})

@login_required
@staff_required
def menu_update(request, pk):
    obj = get_object_or_404(MenuItem, pk=pk)
    form = MenuItemForm(request.POST or None, instance=obj)
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
