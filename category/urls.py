from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('categories/', include('category.urls')),  # یا هر پیشوندی که مد نظرتان است
]