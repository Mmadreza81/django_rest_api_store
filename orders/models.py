from django.db import models
from home.models import Product
from decimal import Decimal
from accounts.models import Address, User
from django.core.validators import MinValueValidator, MaxValueValidator

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True, blank=True, related_name='aorders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    discount = models.IntegerField(blank=True, null=True, default=None)
    status = models.CharField(max_length=32, default='Pending', choices=[
        ('Pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ])

    class Meta:
        ordering = ('paid_at', '-updated_at', 'status')

    def __str__(self):
        return f'{self.user} - {str(self.id)}'

    def get_total_price(self):
        total = sum(item.line_total for item in self.items.all())

        if self.discount:
            discount_price = (Decimal(self.discount) / Decimal('100')) * total
            return total - discount_price
        return total

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    unit_price = models.DecimalField(max_digits=20, decimal_places=0)
    quantity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(90)])
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.code

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    def get_total_price(self):
        total = sum(item.line_total for item in self.items.all())

        if self.coupon:
            discount_price = (Decimal(self.coupon.discount) / Decimal('100')) * total
            return total - discount_price
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.quantity * self.product.price

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'
