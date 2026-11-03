from django.urls import path
from .views import (
    DiscountListCreateView,
    DiscountDetailView,
    ApplyDiscountView,
)

urlpatterns = [
    path('', DiscountListCreateView.as_view(), name='discount-list-create'),
    path('<int:pk>/', DiscountDetailView.as_view(), name='discount-detail'),
    path('apply/', ApplyDiscountView.as_view(), name='apply-discount'),
]