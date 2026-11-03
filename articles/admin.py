from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'reading_time', 'author', 'created_date')
    list_filter = ('status', 'category', 'created_date')
    search_fields = ('title', 'summary_context', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['category']
    readonly_fields = ('created_date', 'updated_date')
    
    # پر شدن خودکار فیلد author با کاربری که در حال ساخت مقاله در ادمین است
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)