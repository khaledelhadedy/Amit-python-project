from django.contrib import admin

# Register your models here.
from .models import Product, Brand, Category, ProductReview


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'brand', 'countInStock', 'description', 'category', 'image','created_at']
    search_fields = ['name', 'brand', 'category']


admin.site.register(Product, ProductAdmin)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(ProductReview)


