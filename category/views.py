from django.shortcuts import render

from rest_framework import viewsets, permissions, filters
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category
from .serializers import CategorySerializer, CategoryCreateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'created_date', 'updated_date']
    ordering = ['name']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = (
            Category.objects
            .filter(is_active=True)
            .select_related('owner', 'parent')
            .prefetch_related('children')
            .annotate(product_count=Count('products'))
        )

        # ?roots=true → فقط کتگوری‌های اصلی (بدون parent)
        if self.request.query_params.get('roots') == 'true':
            queryset = queryset.filter(parent__isnull=True)

        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateSerializer
        return CategorySerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]