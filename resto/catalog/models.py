from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=80, unique=True)  # MAIN, APP, DRINK
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    category = models.ForeignKey('catalog.Category', on_delete=models.PROTECT, related_name='items')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_qty = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.name} ({self.category.code})"

class StockMovement(models.Model):
    MOVE_IN = 'IN'
    MOVE_OUT = 'OUT'
    MOVE_ADJUST = 'ADJUST'
    MOVE_CHOICES = [(MOVE_IN,'IN'), (MOVE_OUT,'OUT'), (MOVE_ADJUST,'ADJUST')]

    menu_item = models.ForeignKey('catalog.MenuItem', on_delete=models.CASCADE, related_name='movements')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    move_type = models.CharField(max_length=6, choices=MOVE_CHOICES)
    qty = models.IntegerField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
