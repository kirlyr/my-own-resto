from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from orders.models import Order


class PaymentMethod(models.Model):
    # Biar ringkas & konsisten, kode cukup pendek (mis. CASH, CARD)
    code = models.CharField(max_length=16, unique=True)  # contoh: "CASH", "CARD"
    name = models.CharField(max_length=80)

    class Meta:
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Payment(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
        db_index=True,
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name="payments",
        db_index=True,
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    # Untuk transaksi kartu: nomor otorisasi/approval code dari EDC
    ref_no = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Approval code EDC (wajib untuk pembayaran kartu)"
    )
    # Simpan 4 digit terakhir kartu; validasi hanya angka 4 digit
    card_last4 = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        validators=[RegexValidator(r"^\d{4}$", "Harus 4 digit angka.")],
        help_text="4 digit terakhir kartu (wajib untuk pembayaran kartu)"
    )
    paid_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-paid_at"]

    def __str__(self):
        return f"Payment #{self.pk} - {self.payment_method.code} - {self.amount_paid}"

    # Validasi logika bisnis: field khusus kartu wajib hanya jika method= CARD
    def clean(self):
        super().clean()
        method_code = (self.payment_method.code if self.payment_method_id else "").upper()

        if method_code == "CARD":
            # Wajib ada ref_no dan card_last4
            if not self.ref_no:
                raise ValidationError({"ref_no": "Wajib diisi untuk pembayaran kartu."})
            if not self.card_last4:
                raise ValidationError({"card_last4": "Wajib diisi untuk pembayaran kartu."})
        elif method_code == "CASH":
            # Untuk tunai, pastikan field kartu tidak diisi
            if self.ref_no:
                raise ValidationError({"ref_no": "Untuk tunai, ref_no harus kosong."})
            if self.card_last4:
                raise ValidationError({"card_last4": "Untuk tunai, card_last4 harus kosong."})

    # Opsional: jaga-jaga kalau disave tanpa full_clean() dari form/admin
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
