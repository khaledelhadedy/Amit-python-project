from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import CartItemSerializer, OrderSerializer, TaxAndShippingRateSerializer
from project.utils import create_response
from product.models import Product
from .models import Order, OrderItem, ShippingAddress, TaxAndShippingRate, Cart, CartItem
from django.db.models import Q
from decimal import Decimal
from django.db.models import F
from project.permissions import IsOwnerOrAdmin
from project.utils import generate_tokens
from django.utils import timezone

class TaxAndShippingRateViewSet(viewsets.ModelViewSet):
    queryset = TaxAndShippingRate.objects.all()
    serializer_class = TaxAndShippingRateSerializer
    permission_classes = [IsAdminUser]  


    def list(self, request, *args, **kwargs):
        tax_and_shipping = TaxAndShippingRate.objects.all()
        if tax_and_shipping.exists():
            serializer = self.get_serializer(tax_and_shipping, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "No tax and shipping configurations found."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartViewSet(viewsets.ModelViewSet):
    
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin] 
    
    def get_queryset(self):
        cart = Cart.objects.filter(user=self.request.user).first()  
        if cart:
            return CartItem.objects.filter(cart=cart)
        return CartItem.objects.none() 
    @action(detail=False, methods=['post'], url_path='add-to-cart/(?P<product_id>[^/.]+)')
    def add_to_cart(self, request, product_id=None):
      
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        quantity = int(request.data.get('quantity', 1))  
        image = request.data.get('image')  

        if not product_id:
            return Response({"message": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        
        if cart_item:
            cart_item.quantity += quantity
            cart_item.image = image if image else cart_item.image  
            cart_item.save()
            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)
        
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity, image=image)
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        user = request.user
        
        cart = Cart.objects.filter(user=user).first()
        if not cart:
            return Response({"message": "No cart found."}, status=status.HTTP_404_NOT_FOUND)

        address_data = request.data.get('shipping_address')
        if not address_data:
            return Response({"message": "Shipping address is required."}, status=status.HTTP_400_BAD_REQUEST)

        shipping_address = ShippingAddress.objects.create(
            user=user,
            address=address_data.get('address'),
            city=address_data.get('city'),
            postalCode=address_data.get('postalCode'),
            country=address_data.get('country')
        )

        tax_shipping_rate = TaxAndShippingRate.objects.filter(
            country=shipping_address.country,
            region=shipping_address.city  
        ).first()

        if not tax_shipping_rate:
            return Response(
                {"message": "The area is outside the shipping range."},
                status=status.HTTP_400_BAD_REQUEST
            )
        total_cart_value = sum([item.product.price * item.quantity for item in cart.items.all()])
        
        tax_price = total_cart_value * (tax_shipping_rate.tax_rate / 100)
        
        if total_cart_value >= tax_shipping_rate.free_shipping_threshold:
            shipping_price = 0.00  
        else:
            shipping_price = tax_shipping_rate.shipping_rate  

        order = Order.objects.create(
            user=user,
            order_status='Pending',
            payment_method=request.data.get('payment_method', 'Cash'),
            taxPrice=tax_price,
            shippingPrice=shipping_price,
            totalPrice=Decimal(total_cart_value) + Decimal(tax_price) + Decimal(shipping_price),
            shipping_address=shipping_address
        )
        for cart_item in cart.items.all():
            product = cart_item.product
            if product.countInStock < cart_item.quantity:
                order.order_status = 'Failed'
                order.save()
                return Response(
                    {"message": f"Not enough stock for product {product.name}. Available: {product.countInStock}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            product.countInStock -= cart_item.quantity
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                unit_price=product.price,
                image=cart_item.image
            )

        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='get-order-by-id')
    def get_order_by_id(self, request, pk=None):
        try:
            order = self.get_object()

            if order.user != request.user and not request.user.is_staff:
                raise PermissionDenied("You do not have permission to view this order.")
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=True, methods=['put'], url_path='update-to-paid')
    def update_order_to_paid(self, request, pk=None):
       
        try:
            order = self.get_object()

            if order.user != request.user:
                raise PermissionDenied("You do not have permission to update this order.")


            order.is_paid = True
            order.order_status = 'Confirmed'
            order.paid_at = timezone.now()
            order.save()

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
    @action(detail=False, methods=['get'], url_path='my-orders')
    def get_my_orders(self, request):
        
        orders = Order.objects.filter(user=request.user)

        if not orders.exists():
            return Response({"message": "No orders found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    @action(detail=True, methods=['put'], url_path='update-to-delivered')
    def update_order_to_delivered(self, request, pk=None):
       
        try:
            order = self.get_object()

            if not request.user.is_staff:
                raise PermissionDenied("You do not have permission to update this order.")

            order.order_status = 'Delivered'         
            order.delivered_at = timezone.now()
            order.save()

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
    @action(detail=False, methods=['get'], url_path='all-orders', permission_classes=[IsAdminUser])
    def get_all_orders(self, request):
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to view all orders.")

        orders = Order.objects.all()
        
           
        if not orders.exists():
            return Response({"message": "No orders found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put'], url_path='cancel-order', permission_classes=[IsOwnerOrAdmin])
    def cancel_order(self, request, pk=None):
        try:
            order = self.get_object()

            if order.user != request.user and not request.user.is_staff:
                raise PermissionDenied("You do not have permission to cancel this order.")

            if order.order_status in ['Delivered', 'Canceled']:
                return Response(
                    {"message": f"Order cannot be canceled as it is already {order.order_status.lower()}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            order.order_status = 'Canceled'
            order.save()

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)