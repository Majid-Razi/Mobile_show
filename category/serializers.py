from rest_framework import serializers
from .models import Category


class CategoryChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'icon']


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(use_url=True, required=False, allow_null=True)
    children = CategoryChildSerializer(many=True, read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'image', 'icon', 'is_active',
            'parent', 'parent_name', 'children',
            'product_count', 'created_date', 'updated_date',
        ]
        read_only_fields = ['created_date', 'updated_date', 'slug']


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'image', 'icon', 'is_active', 'parent']
        extra_kwargs = {
            'slug': {'required': False},
        }

    def validate_name(self, value):
        owner = self.context['request'].user
        if Category.objects.filter(name=value, owner=owner).exists():
            raise serializers.ValidationError('این کتگوری قبلاً ساخته شده.')
        return value

    def validate_parent(self, value):
        if value and value.parent:
            raise serializers.ValidationError('حداکثر دو سطح کتگوری مجاز است.')
        return value

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)