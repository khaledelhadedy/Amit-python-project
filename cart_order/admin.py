
# Register your models here.
from django.contrib import admin
from .models import  Order, OrderItem, TaxAndShippingRate, Cart, CartItem



class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_method', 'order_status', 'delivered_at', 'is_paid', 'paid_at', 'shipping_address','taxPrice', 'shippingPrice', 'totalPrice', 'createdAt']

class TaxAndShippingRateAdmin(admin.ModelAdmin):
    list_display = ['id', 'country', 'region', 'tax_rate', 'shipping_rate']


class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'createdAt']
    
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'unit_price']


admin.site.register(OrderItem, OrderItemAdmin) 
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(TaxAndShippingRate, TaxAndShippingRateAdmin)


