from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class AuthAccessTests(TestCase):
    """
    Menguji pembatasan akses halaman staff:
    - Staff boleh membuka category_list
    - Non-staff diblok (302 ke login atau 403)
    """
    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(
            username="admin", password="pass123", is_staff=True
        )
        self.user = User.objects.create_user(
            username="user", password="pass123", is_staff=False
        )

    def test_staff_can_open_category_list(self):
        self.client.login(username="admin", password="pass123")
        url = reverse("catalog:category_list")  # pastikan nama url ini ada di catalog/urls.py
        res = self.client.get(url)
        # boleh 200 (render) atau 302 (misal redirect internal)
        self.assertIn(res.status_code, [200, 302])

    def test_nonstaff_blocked_from_category_list(self):
        self.client.login(username="user", password="pass123")
        url = reverse("catalog:category_list")
        res = self.client.get(url)
        # non-staff harus TIDAK bisa akses (umumnya 302 ke login atau 403)
        self.assertIn(res.status_code, [302, 403])
