from django.urls import path, include
from rest_framework import routers
from .views import LoginViewSet, RegisterViewSet, UserProfileViewSet, UsersViewSet

router = routers.DefaultRouter()
router.register('login', LoginViewSet, basename='login', )
router.register('register', RegisterViewSet, basename='register', )
router.register('profile', UserProfileViewSet, basename='profile', )
router.register('users', UsersViewSet, basename='users', )

urlpatterns = [
    path('', include(router.urls)),
]