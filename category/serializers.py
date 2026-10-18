from rest_framework import serializers
from .models import Category


class CategoryChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'icon']


class CategorySerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.username') # نمایش نام سازنده در خروجی
    product_count = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(use_url=True, required=False, allow_null=True)
    children = CategoryChildSerializer(many=True, read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'owner', 'owner_name', 'name', 'slug', 'image', 'icon', 'is_active',
            'parent', 'parent_name', 'children',
            'product_count', 'created_date', 'updated_date',
        ]
        read_only_fields = ["id", "owner", "created_date", "updated_date", "slug"]

class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'icon', 'is_active', 'parent']
        read_only_fields = ['id']
        extra_kwargs = {
            'slug': {'required': False},
        }

    def validate_name(self, value):
        owner = self.context['request'].user
        queryset = Category.objects.filter(name=value, owner=owner)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('This category already exists.')
        return value

    def validate_parent(self, value):
        if value and value.parent:
            raise serializers.ValidationError('A maximum of two category levels is allowed.')
        if self.instance and value == self.instance:
            raise serializers.ValidationError('A category cannot be its own parent.')
        return value