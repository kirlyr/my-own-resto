# Test Plan — Sistem Resto (Django)  
Tanggal: 2025-09-27

## 1. Tujuan
Memastikan unit program utama (Catalog, Orders, Payments, Public Cart/Checkout, POS) berjalan sesuai kebutuhan: CRUD data, alur pemesanan pelanggan, perhitungan subtotal/pajak/diskon, dan proses checkout.

## 2. Lingkup Uji
- **Catalog**: Category & MenuItem (CRUD, filter, pagination, stok & restock).
- **Public**: Menu pelanggan, keranjang (tambah/ubah/hapus), checkout.
- **Orders**: Pembuatan Order/OrderItem, update status.
- **Payments**: Metode pembayaran tersedia, redirect ke halaman pembayaran/checkout.
- **Reports**: Ringkas verifikasi page render (jika ada).
- **Auth & Roles**: Akses staff vs non-staff.

## 3. Kebutuhan Uji (Requirements Sederhana)
- Staff dapat kelola **Category** dan **MenuItem** (CRUD).
- Menu pelanggan menampilkan item aktif; tombol **Tambah** menambah ke keranjang (session).
- Keranjang dapat **update qty** dan **hapus item** dengan validasi stok.
- Checkout membuat **Order** (status awal DRAFT/PLACED) dan mengarahkan ke **pembayaran**.
- Perhitungan **subtotal**, **tax**, **discount**, **grand total** konsisten.
- **PaymentMethod** minimal satu (mis. CASH) tersedia saat checkout.
- URL names konsisten dengan `catalog.urls` dan `resto/urls.py` (namespace `catalog`).

## 4. Skenario Uji (tingkat tinggi)
1. **CRUD Category** — tambah, ubah, hapus; validasi kode unik.
2. **CRUD MenuItem** — tambah menu, set harga & stok, restock (StockMovement jika ada), nonaktif menu.
3. **Public Menu** — pencarian & filter kategori; tombol “Tambah” memasukkan ke keranjang.
4. **Cart** — tampil ringkasan, ubah qty, hapus item, cek subtotal.
5. **Checkout** — pilih metode bayar, submit → Order dibuat & dialihkan ke halaman pembayaran.
6. **POS** (jika digunakan) — create order, add item, checkout.
7. **Auth** — halaman staff tidak bisa diakses user biasa.
8. **Regression URL** — pastikan semua `{% url %}` dengan `catalog:...` sesuai.

## 5. Data Uji
### Akun
- **admin** (staff/is_staff=True): untuk CRUD & POS.
- **user** (bukan staff): untuk alur public.

### Master Data
- Category: **MAIN** (Masakan), **DRINK** (Minuman).
- MenuItem:
  - Nasi Goreng — price 20000, stok 20, aktif.
  - Es Teh — price 5000, stok 50, aktif.
- PaymentMethod: **CASH** (Tunai).

## 6. Lingkungan & Alat
- Django 5.x, SQLite default.
- Browser Chrome (manual), Django `Client` (otomasi).
- `pytest` + `pytest-django` (opsional), atau `manage.py test` bawaan.

## 7. Strategi & Jenis Uji
- **Unit test** (model methods, view minimal 200/302/403).
- **Integration/functional** (session cart → checkout).
- **Manual test** untuk UX (tampilan, notifikasi, gambar).

## 8. Kriteria Masuk/Keluar
- **Masuk**: App migrasi sukses, superuser dibuat, data uji terpasang.
- **Keluar**: Seluruh test pass; blocker/critical 0; mayoritas minor diakui/dicatatan.

## 9. Dokumentasi Hasil Uji
Gunakan **CSV Test Cases** yang disiapkan + bukti (screenshot/console). Untuk setiap test, isi kolom *Status* (PASS/FAIL) dan *Evidence* (path gambar/log).
