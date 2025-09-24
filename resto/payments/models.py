from django.db import models, transaction
from orders.models import Order


class PaymentMethod(models.Model):
    code = models.CharField(max_length=50, unique=True) # CASH, CARD
    name = models.CharField(max_length=80)


    def __str__(self):
        return self.name


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    ref_no = models.CharField(max_length=50, blank=True) # kode otorisasi EDC
    card_last4 = models.CharField(max_length=4, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)