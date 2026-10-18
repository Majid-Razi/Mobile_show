from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'owner', 'is_active', 'product_count', 'created_date']
    list_filter = ['is_active', 'parent', 'created_date']
    search_fields = ['name', 'slug', 'owner__username']
    
    # ۱. اضافه کردن owner به فیلدهای فقط-خواندنی
    readonly_fields = ['owner', 'created_date', 'updated_date', 'product_count']
    
    list_editable = ['is_active']
    list_per_page = 20
    prepopulated_fields = {'slug': ('name',)}

    # ۲. ذخیره خودکار کاربر لاگین‌شده به عنوان owner هنگام ساخت رکورد جدید
    def save_model(self, request, obj, form, change):
        if not change or not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)