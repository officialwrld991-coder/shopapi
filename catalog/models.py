import uuid

from django.db import models
from django.db.models import F, Q
from django.core.validators import MinValueValidator

from common.models import TimestampedModel


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(TimestampedModel):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    sku = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "category"]),
        ]

    def __str__(self):
        return self.title


class Inventory(models.Model):
    product = models.OneToOneField(Product, related_name="inventory", on_delete=models.CASCADE, primary_key=True)
    quantity_on_hand = models.PositiveIntegerField(default=0)
    quantity_reserved = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "inventory"
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity_reserved__lte=F("quantity_on_hand")),
                name="inventory_reserved_lte_on_hand",
            ),
        ]

    @property
    def available(self):
        return self.quantity_on_hand - self.quantity_reserved

    @property
    def is_low_stock(self):
        return self.available <= self.low_stock_threshold


class Cart(TimestampedModel):
    cart_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f" {self.cart_id}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="+", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="cartitem_unique_product_per_cart",
            ),
        ]

    @property
    def line_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"