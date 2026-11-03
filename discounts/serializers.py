from rest_framework import serializers
from .models import Discount


class DiscountSerializer(serializers.ModelSerializer):
    product_title = serializers.ReadOnlyField(source='sppicific_product.title')
    customer_username = serializers.ReadOnlyField(source='spicific_customer.username')

    class Meta:
        model = Discount
        fields = [
            'id', 'code', 'description', 'value_type', 'Value',
            'discount_cont', 'used_count', 'min_order_amount', 'max_usage',
            'sppicific_product', 'product_title', 'spicific_customer', 'customer_username',
            'first_buying', 'expired_date', 'status', 'created_date'
        ]
        read_only_fields = ['id', 'used_count', 'created_date']


class ApplyDiscountSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    cart_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    product_id = serializers.IntegerField(required=False, allow_null=True)