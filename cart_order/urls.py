from django.urls import path, include
from rest_framework import routers
from .views import CartViewSet,TaxAndShippingRateViewSet, OrderViewSet

router = routers.DefaultRouter()

router.register(r'tax-and-shipping', TaxAndShippingRateViewSet, basename='tax-and-shipping')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'order', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]