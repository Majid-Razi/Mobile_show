from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'owner', 'is_active', 'product_count', 'created_date']
    list_filter = ['is_active', 'parent', 'created_date']
    search_fields = ['name', 'slug', 'owner__username']
    readonly_fields = ['created_date', 'updated_date', 'product_count']
    list_editable = ['is_active']
    list_per_page = 20
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'تعداد محصولات'