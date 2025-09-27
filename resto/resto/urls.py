from django.contrib import admin
from django.urls import path, include
from orders.views import dashboard, pos_create_order, pos_add_item, pos_checkout
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from reports.views import sales_monthly, top_items_weekly

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', dashboard, name='dashboard'),

    # === KATALOG + PUBLIC (pakai namespace 'catalog') ===
    path('', include(('catalog.urls', 'catalog'), namespace='catalog')),

    # POS (kasir)
    path('pos/create/', pos_create_order, name='pos_create_order'),
    path('pos/<str:order_no>/add-item/', pos_add_item, name='pos_add_item'),
    path('pos/<str:order_no>/checkout/', pos_checkout, name='pos_checkout'),

    # Laporan
    path('reports/monthly/', sales_monthly, name='sales_monthly'),
    path('reports/top-weekly/', top_items_weekly, name='top_items_weekly'),

    # Orders (route lain milik kasir)
    path('', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
