from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from project.utils import generate_tokens
from .models import Cart, CartItem, Order, OrderItem, ShippingAddress, TaxAndShippingRate
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer() 

    class Meta:
        model = Order
        fields = '__all__'


class TaxAndShippingRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxAndShippingRate
        fields = '__all__'
