from django.urls import path, include
from rest_framework import routers
from .views import CategoryViewSet, BrandViewSet, ProductViewSet, ProductReviewViewSet
router = routers.DefaultRouter()
router.register('category', CategoryViewSet, basename='category', )
router.register('brand', BrandViewSet, basename='brand', )
router.register('product', ProductViewSet, basename='product', )
router.register(r'product/(?P<product_id>[^/.]+)/reviews', ProductReviewViewSet, basename='product-review')


urlpatterns = [
    path('', include(router.urls)),
]