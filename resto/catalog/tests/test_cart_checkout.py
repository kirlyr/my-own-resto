from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from catalog.models import Category, MenuItem
from payments.models import PaymentMethod


class CartFlowTests(TestCase):
    """
    Menguji alur publik:
    - Lihat menu publik
    - Tambah item ke keranjang
    - Lihat keranjang
    - Update qty item
    - Checkout dengan metode CASH
    """
    def setUp(self):
        self.client = Client()

        # Data master
        self.cat = Category.objects.create(name="Masakan", code="MAIN")
        self.item = MenuItem.objects.create(
            category=self.cat,
            name="Nasi Goreng",
            price=Decimal("20000"),
            stock_qty=20,
            is_active=True,
        )
        PaymentMethod.objects.create(code="CASH", name="Tunai")

        # (opsional) user biasa untuk menguji halaman publik login-required/anonymous
        self.user = User.objects.create_user(username="cust", password="pass123", is_staff=False)

    def test_public_menu_add_update_checkout(self):
        # 1) Halaman menu publik harus bisa dibuka
        res = self.client.get(reverse("catalog:public_menu"))
        self.assertEqual(res.status_code, 200)

        # 2) Tambah ke keranjang
        add_url = reverse("catalog:cart_add", args=[self.item.id])
        res = self.client.post(add_url, follow=True)
        self.assertIn(res.status_code, [200, 302])

        # 3) Lihat keranjang
        cart_url = reverse("catalog:cart_view")
        res = self.client.get(cart_url)
        self.assertEqual(res.status_code, 200)
        # Opsional: cek teks nama item ada di halaman (jika template menampilkan)
        self.assertContains(res, "Nasi Goreng", status_code=200)

        # 4) Update qty menjadi 3
        update_url = reverse("catalog:cart_update", args=[self.item.id])
        res = self.client.post(update_url, {"qty": 3}, follow=True)
        self.assertIn(res.status_code, [200, 302])

        # 5) Checkout dengan payment_method=CASH
        checkout_url = reverse("catalog:cart_checkout")
        res = self.client.post(checkout_url, {"payment_method": "CASH"}, follow=True)
        # Boleh 200 (tampil halaman sukses) atau 302 (redirect ke halaman pembayaran)
        self.assertIn(res.status_code, [200, 302])
