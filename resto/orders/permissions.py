from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy

def _is_kasir(user):
    # Boleh akses jika login dan user adalah staff atau anggota grup "Kasir"
    return user.is_authenticated and (user.is_staff or user.groups.filter(name='Kasir').exists())

def kasir_required(view_func=None):
    decorator = user_passes_test(_is_kasir, login_url=reverse_lazy('login'))
    return decorator if view_func is None else decorator(view_func)
