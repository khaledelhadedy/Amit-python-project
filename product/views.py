from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import BrandSerializer,CategorySerializer, ProductSerializer, ProductReviewSerializer
from project.utils import create_response, generate_tokens
from .models import Product, Brand, Category, ProductReview
from django.db.models import Q
from project.permissions import IsOwnerOrAdmin
# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUser]
    
    
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        if self.action in ['create','destroy', 'partial_update']:  
            return [IsAdminUser()]
        return [AllowAny()]
    def list(self, request):
        keyword = request.query_params.get('search', '')

        if keyword:
            products = Product.objects.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(brand__name__icontains=keyword) |
                Q(category__name__icontains=keyword)
            )
        else:
            products = Product.objects.all()

        serializer = ProductSerializer(products, many=True)

        return Response(
            {
                "message": "Products retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )
        
    def retrieve(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')  

        product = Product.objects.filter(id=product_id).first()

        if not product:
            return create_response(
                message="Product not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        return create_response(
            message="Product Retrieved successfully.",
            data=ProductSerializer(product).data,
            status_code=status.HTTP_200_OK
        )
        
    def destroy(self, request, *args, **kwargs, ):
        product_id = kwargs.get('pk')  

        product = Product.objects.filter(id=product_id).first()

        if not product:
            return create_response(
                message="Product not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        product.delete()
        return create_response(
            message="Product deleted successfully.",
            status_code=status.HTTP_200_OK
        )
        
        
    def create(self, request, *args, **kwargs):
        product_name = request.data.get("name")
        if Product.objects.filter(name=product_name).exists():
            return Response(
            {"message": "Product with this name already exists."},
            status=status.HTTP_400_BAD_REQUEST,)
        serializer = ProductSerializer(data=request.data)
        
        if serializer.is_valid():
            product = serializer.save()
            
            return Response(
                {
                    "message": "Product created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        
        return Response(
            {"message": "Validation error.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
        
    def partial_update(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(product, data=request.data, partial=True) 
        
        if serializer.is_valid():
            product = serializer.save()

            return Response(
                {
                    "message": "Product updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        
        return Response(
            {"message": "Validation error.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
        
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], url_path='upload-image')
    def upload_image(self, request, *args, **kwargs):
        product = self.get_object()
        
        if 'image' not in request.FILES:
            return Response(
                {"message": "No image file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image = request.FILES['image']
        product.image = image
        product.save()
        
        serializer = ProductSerializer(product)

        return Response(
            {
                "message": "Product image uploaded successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
   
    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data, context={'request': request, 'product': product})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {
                "message": "Review created successfully.", 
                "data": serializer.data, 
                "total_reviews": product.total_reviews(),  
                'avg_rating': product.avg_rating(), 
            },
            status=status.HTTP_201_CREATED
        )
        
    def list(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        reviews = ProductReview.objects.filter(product=product)
        serializer = self.get_serializer(reviews, many=True)
        return Response(
            {
                "message": "Reviews retrieved successfully.", 
                "data": serializer.data, 
                "total_reviews": product.total_reviews(),  
                'avg_rating': product.avg_rating(),       
            },
            status=status.HTTP_200_OK
        )
