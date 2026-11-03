from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from .models import Discount
from .serializers import DiscountSerializer, ApplyDiscountSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="You must be logged in to perform this action.")
        if not request.user.is_staff:
            raise PermissionDenied(detail="Only admins can manage discounts.")
        return True


# ۱. لیست و ساخت کدهای تخفیف (مدیریت توسط ادمین)
class DiscountListCreateView(generics.ListCreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAdminOrReadOnlyPermission]
    authentication_classes = [CsrfExemptSessionAuthentication]


# ۲. جزئیات، ویرایش و حذف کد تخفیف
class DiscountDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAdminOrReadOnlyPermission]
    authentication_classes = [CsrfExemptSessionAuthentication]
    lookup_field = 'pk'


# ۳. اعتبارسنجی و اعمال کد تخفیف برای سبد خرید
class ApplyDiscountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def post(self, request):
        serializer = ApplyDiscountSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            cart_total = serializer.validated_data['cart_total']
            product_id = serializer.validated_data.get('product_id')
            user = request.user

            try:
                discount = Discount.objects.get(code=code)
            except Discount.DoesNotExist:
                return Response({"error": "Invalid discount code."}, status=status.HTTP_404_NOT_FOUND)

            # بررسی اعتبار کلی
            if not discount.is_valid():
                return Response({"error": "This discount code is expired, inactive, or exhausted."}, status=status.HTTP_400_BAD_REQUEST)

            # بررسی مشتری خاص
            if discount.spicific_customer and discount.spicific_customer != user:
                return Response({"error": "This discount code is not valid for your account."}, status=status.HTTP_403_FORBIDDEN)

            # بررسی محصول خاص
            if discount.sppicific_product:
                if not product_id or int(product_id) != discount.sppicific_product.id:
                    return Response({"error": f"This code is only valid for product: {discount.sppicific_product.title}"}, status=status.HTTP_400_BAD_REQUEST)

            # بررسی حداقل مبلغ سفارش
            if discount.min_order_amount and cart_total < discount.min_order_amount:
                return Response({
                    "error": f"Minimum order amount for this code is {discount.min_order_amount}."
                }, status=status.HTTP_400_BAD_REQUEST)

            # محاسبه تخفیف
            if discount.value_type == Discount.ValueType.PERCENTAGE:
                discount_amount = (cart_total * discount.Value) / 100
            else:
                discount_amount = discount.Value

            if discount_amount > cart_total:
                discount_amount = cart_total

            final_total = cart_total - discount_amount

            return Response({
                "message": "Discount applied successfully!",
                "code": discount.code,
                "discount_amount": discount_amount,
                "final_total": final_total
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)