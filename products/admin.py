from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'created_date')
    search_fields = ('title', 'slug')
    list_filter = ('category', 'created_date')