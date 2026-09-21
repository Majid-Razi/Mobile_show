from django.contrib import admin
from django.db.models.functions import Log
from django.urls import path, include
from .views import RegisterView, LoginView, LogoutView, ChangePasswordView, RefreshTokenView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path("refresh/", RefreshTokenView.as_view(), name = "jwt-refresh"),


]