from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg
from core.models import CustomUser
# Create your models here.
class Category(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    
class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default= 'Product')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)
    countInStock = models.PositiveIntegerField(default=0)
    description = models.TextField(default='', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='products/', default='products/default.png')
      
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def total_reviews(self):
        return ProductReview.objects.filter(product=self).count()
    
    def avg_rating(self):
        reviews = ProductReview.objects.filter(product=self)
        if reviews.exists():
            return reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return None
    
    def is_in_stock(self):
        return self.countInStock > 0
    
    
    
class ProductReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class meta:
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"Review for {self.product.name} by {self.user.full_name}"
    
   