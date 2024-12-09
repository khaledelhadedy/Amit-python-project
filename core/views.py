from rest_framework import viewsets, status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializers import UserLoginSerializer, UserSerializer
from .models import CustomUser
from django.db.models import Q
from project.permissions import IsOwnerOrAdmin
from project.utils import generate_tokens, create_response

@method_decorator(csrf_exempt, name='dispatch')
class RegisterViewSet(viewsets.ModelViewSet):
    http_method_names = ['post']
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            tokens = generate_tokens(user)
            return create_response(
                message="User created successfully.",
                data={
                    "user": UserSerializer(user).data,
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                },
                status_code=status.HTTP_201_CREATED,
            )
        return create_response(
            message="Validation error.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@method_decorator(csrf_exempt, name='dispatch')
class LoginViewSet(viewsets.ViewSet):
    http_method_names = ['post']
    permission_classes = [AllowAny] 
    def create(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = generate_tokens(user)

            return create_response(
                message=f"Login successful, Hi {user.full_name}!",
                data={
                    "user": UserSerializer(user).data,
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                },
                status_code=status.HTTP_200_OK,
            )

        return create_response(
            message="Login failed. Please check your credentials.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
class UserProfileViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return create_response(
            message="User profile retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            updated_user = serializer.save()

            tokens = generate_tokens(updated_user)
            return create_response(
                message="User profile updated successfully.",
                data={
                    "user": UserSerializer(updated_user).data,
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                },
                status_code=status.HTTP_200_OK,
            )

        return create_response(
            message="Validation error.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        
class UsersViewSet(viewsets.ModelViewSet):
    http_method_names = ['delete', 'get', 'patch']

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = CustomUser.objects.filter(id=user_id).first()

        if not user:
            return create_response(
                message="User not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        user.delete()
        return create_response(
            message="User deleted successfully.",
            status_code=status.HTTP_200_OK
        )

    def retrieve(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = CustomUser.objects.filter(id=user_id).first()

        if not user:
            return create_response(
                message="User not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        return create_response(
            message="User Retrieved successfully.",
            data=UserSerializer(user).data,
            status_code=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = CustomUser.objects.filter(id=user_id).first()

        if not user:
            return create_response(
                message="User not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            tokens = generate_tokens(updated_user)
            return create_response(
                message="User updated successfully.",
                data={
                    "user": UserSerializer(updated_user).data,
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                },
                status_code=status.HTTP_200_OK
            )
        return create_response(
            message="Validation error.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

        





