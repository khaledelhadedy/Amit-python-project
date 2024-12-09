
from rest_framework import serializers
from .models import Product, Category, Brand, ProductReview
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg
from django.conf import settings

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'  
        
    
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'    

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
    
    def validate_name(self, value):
        if value == "":
            raise serializers.ValidationError(_('Name cannot be empty'))
        return value
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError(_('Price cannot be negative'))
        return value
    
    
    def validate_countInStock(self, value):
        if value < 0:
            raise serializers.ValidationError(_('Count in stock cannot be negative'))
        return value
        
        
    def validate_image(self, value):
        if value and value.size > settings.MAX_IMAGE_SIZE:
            raise serializers.ValidationError(_('Image size cannot exceed 5MB'))
        return value
        
      
class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True},   
            'product': {'read_only': True} 
        }

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')  
        product = self.context.get('product')

        if ProductReview.objects.filter(product=product, user=request.user).exists():
            raise serializers.ValidationError(
                {"message": "You have already reviewed this product."}
            )

        return ProductReview.objects.create(
            product=product,
            user=request.user,
            **validated_data
        )

        