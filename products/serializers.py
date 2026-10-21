from rest_framework import serializers
from .models import Product
from category.serializers import CategorySerializer # برای نمایش اطلاعات کامل کتگوری در صورت نیاز

class ProductSerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    # اگر خواستید جزئیات کامل کتگوری را نمایش دهید، می‌توانید خط زیر را فعال کنید:
    # category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'owner', 'owner_name', 'category', 'category_name',
            'name', 'slug', 'price', 'stock', 'is_active',
            'description', 'image', 'created_date', 'updated_date'
        ]
        read_only_fields = ['id', 'owner', 'created_date', 'updated_date', 'slug']


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'price', 
            'stock', 'is_active', 'description', 'image'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'slug': {'required': False},
        }

    # بررسی تکراری نبودن نام محصول برای هر کاربر یا به صورت کلی
    def validate_name(self, value):
        queryset = Product.objects.filter(name=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('A product with this name already exists.')
        return value