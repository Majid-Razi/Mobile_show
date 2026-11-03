from rest_framework import generics, permissions, filters
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from .models import Article
from .serializers import ArticleSerializer, ArticleCreateSerializer


# کلاس کمکی برای عبور دادن درخواست‌های لاگین‌نشده جهت نمایش خطای دقیق
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


# کلاس دسترسی ادمین با پیام‌های خطای انگلیسی سفارشی
class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="You must be logged in to perform this action.")
        if not request.user.is_staff:
            raise PermissionDenied(detail="Only admins can create, update, or delete articles.")
        return True


# ۱. لیست مقالات (GET) با قابلیت جستجو و مرتب‌سازی
class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.select_related('author')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_date', 'title']
    ordering = ['-created_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        # کاربران عادی فقط مقالات منتشرشده را می‌بینند، ادمین‌ها همه را می‌بینند
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(status=Article.Status.PUBLISHED)
        return queryset


# ۲. ساخت مقاله جدید (POST)
class ArticleCreateView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleCreateSerializer
    permission_classes = [IsAdminOrReadOnlyPermission]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# ۳. نمایش جزئیات یک مقاله (GET) بر اساس pk
class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.select_related('author')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'


# ۴. ویرایش مقاله (PUT / PATCH)
class ArticleUpdateView(generics.UpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleCreateSerializer
    permission_classes = [IsAdminOrReadOnlyPermission]
    authentication_classes = [CsrfExemptSessionAuthentication]
    lookup_field = 'pk'


# ۵. حذف مقاله (DELETE)
class ArticleDeleteView(generics.DestroyAPIView):
    queryset = Article.objects.all()
    permission_classes = [IsAdminOrReadOnlyPermission]
    authentication_classes = [CsrfExemptSessionAuthentication]
    lookup_field = 'pk'