from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from core.models import CustomUser
from product.models import Product
# Create your models here.
class TaxAndShippingRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  
    shipping_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0) 
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default= Decimal('1500.00'))  
    
    class Meta:
        unique_together = ('country', 'region')

    def __str__(self):
        return f"{self.country} - {self.region or 'General'}"
    
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart of {self.user}"
    
class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)
    image = models.URLField(null=True, blank=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Item {self.product.name} in Cart {self.cart}"
    



class ShippingAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postalCode = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    shippingPrice = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Address of {self.user}: {self.address}"
    
      
class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
        ('Canceled', 'Canceled'),
        ('Confirmed', 'Confirmed'),
        ('Delivered', 'Delivered'),
    )
    
    ORDER_PAYMENT_CHOICES = (
        ('Cash', 'Cash'),
        ('Card', 'Card'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='Pending')
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=10, choices=ORDER_PAYMENT_CHOICES, default='Cash')
    taxPrice = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shippingPrice = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE)
    delivered_at = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} by {self.user}"

    class Meta:
        ordering = ['-createdAt']

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.URLField(null=True, blank=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Item {self.product.name} in Order {self.order}"


