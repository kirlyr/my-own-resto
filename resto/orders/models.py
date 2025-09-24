from django.db import models
from django.conf import settings
from catalog.models import MenuItem

class Customer(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_DRAFT = 'DRAFT'
    STATUS_PLACED = 'PLACED'
    STATUS_PAID = 'PAID'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'DRAFT'),
        (STATUS_PLACED, 'PLACED'),
        (STATUS_PAID, 'PAID'),
        (STATUS_CANCELLED, 'CANCELLED'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)  # kasir yang input
    customer = models.ForeignKey('orders.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    order_no = models.CharField(max_length=30, unique=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PLACED)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    placed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_no

    def recalc_totals(self):
        agg = self.items.aggregate(
            subtotal=models.Sum(models.F('qty') * models.F('price'))
        )
        self.subtotal = agg['subtotal'] or 0
        self.tax_amount = self.subtotal * 0.10
        self.grand_total = self.subtotal + self.tax_amount - self.discount_amount
        self.save(update_fields=['subtotal','tax_amount','grand_total'])

class OrderItem(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.line_total = self.qty * self.price
        super().save(*args, **kwargs)
