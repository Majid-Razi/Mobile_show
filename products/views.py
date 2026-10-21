from rest_framework import generics, permissions, filters
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from .models import Product
from .serializers import ProductSerializer, ProductCreateSerializer


# کلاس کمکی برای جلوگیری از خطای CSRF در تست‌های API (مشابه بخش کتگوری)
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


# کلاس دسترسی: مشاهده آزاد، تغییرات فقط مخصوص ادمین با پیام‌های خطای دلخواه
class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="You must be logged in to perform this action.")
        if not request.user.is_staff:
            raise PermissionDenied(detail="Only admins can create, update, or delete products.")
        return True


# ۱. لیست محصولات (GET) با قابلیت فیلتر، سرچ و مرتب‌سازی
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.select_related('category', 'owner')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_date', 'stock']
    ordering = ['-created_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # کاربران عادی فقط محصولات فعال را می‌بینند، ادمین‌ها همه را می‌بینند
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)

        # فیلتر بر اساس کتگوری (مثلاً ?category=id یا ?category_slug=...)
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset


# ۲. ساخت محصول جدید (POST)
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [IsAdminOrReadOnlyPermission]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# ۳. نمایش جزئیات یک محصول (GET) بر اساس pk یا slug
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related('category', 'owner')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'  # یا اگر می‌خواهید با slug باشد می‌توانید تغییر دهید


# ۴. ویرایش محصول (PUT / PATCH)
class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [IsAdminOrReadOnlyPermission]
    authentication_classes = [CsrfExemptSessionAuthentication]
    lookup_field = 'pk'


# ۵. حذف محصول (DELETE)
class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAdminOrReadOnlyPermission]
    authentication_classes = [CsrfExemptSessionAuthentication]
    lookup_field = 'pk'