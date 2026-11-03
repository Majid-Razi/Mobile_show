from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Article
        fields = [
            'id', 'author', 'author_name', 'title', 'slug', 
            'content', 'image',  
            'created_date', 'updated_date'
        ]
        read_only_fields = ['id', 'author', 'created_date', 'updated_date', 'slug']


class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 
            'image', 'created_date', 'updated_date'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'slug': {'required': False},
        }

    # بررسی تکراری نبودن عنوان مقاله
    def validate_title(self, value):
        queryset = Article.objects.filter(title=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('An article with this title already exists.')
        return value