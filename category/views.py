from rest_framework import generics, permissions, filters
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from .models import Category
from .serializers import CategorySerializer, CategoryCreateSerializer
from rest_framework.authentication import SessionAuthentication


# کلاس کمکی برای عبور دادن درخواست‌های لاگین‌نشده به پرمیشن
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

# کلاس بررسی دسترسی ادمین با پیام‌های دلخواه
class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="You must be logged in to perform this action.")
        if not request.user.is_staff:
            raise PermissionDenied(detail="Only admins can create, update, or delete categories.")
        return True


# ۱. لیست کردن تمام کتگوری‌ها (GET)
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.select_related('owner', 'parent').prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'created_date', 'updated_date']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        # کاربران عادی فقط کتگوری‌های فعال را می‌بینند
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)
        # فیلتر کتگوری‌های اصلی: ?roots=true
        if self.request.query_params.get('roots') == 'true':
            queryset = queryset.filter(parent__isnull=True)
        return queryset


# ۲. ساخت کتگوری جدید (POST)
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    permission_classes = [IsAdminOrReadOnlyPermission]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# ۳. نمایش جزئیات یک کتگوری (GET) بر اساس pk
class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.select_related('owner', 'parent').prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'


# ۴. ویرایش کتگوری (PUT / PATCH) بر اساس pk
class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    permission_classes = [IsAdminOrReadOnlyPermission]
    lookup_field = 'pk'


# ۵. حذف کتگوری (DELETE) بر اساس pk
class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    permission_classes = [IsAdminOrReadOnlyPermission]
    lookup_field = 'pk'