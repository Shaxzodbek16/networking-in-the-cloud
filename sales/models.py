from django.db import models
from django.conf import settings
from django.utils import timezone
from inventory.models import Product
from decimal import Decimal


class Sale(models.Model):
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    datetime = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-datetime"]

    def __str__(self):
        return f"Sale #{self.id} – {self.datetime:%Y-%m-%d %H:%M}"

    def recalc_total(self):
        self.total = sum(item.line_total for item in self.items.all())
        self.save(update_fields=["total"])


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot
    line_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # snapshot price first time
        if not self.pk:
            self.price = self.product.sell_price
        self.line_total = (self.price * Decimal(self.quantity)).quantize(
            Decimal("0.01")
        )
        super().save(*args, **kwargs)

        # Decrease inventory the first time this item is created
        if kwargs.get("force_update", False) is False and self.quantity:
            self.product.quantity = max(0, self.product.quantity - self.quantity)
            self.product.save(update_fields=["quantity"])

        # update parent total
        self.sale.recalc_total()
