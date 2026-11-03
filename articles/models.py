from django.conf import settings
from django.db import models
from django.utils.text import slugify
from category.models import Category  # ارتباط با اپلیکیشن دسته‌بندی‌ها


class Article(models.Model):
    # وضعیت‌های مختلف مقاله
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'

    # اطلاعات پایه
    title = models.CharField(max_length=255, unique=True, verbose_name="Title")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    
    # دسته‌بندی مقاله (ارتباط با اپ Category)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='articles', 
        verbose_name="Category"
    )
    
    # محتوا و خلاصه
    summary_context = models.TextField(blank=True, null=True, verbose_name="Summary Context")
    content = models.TextField(verbose_name="Main Content") # متن کامل مقاله
    
    # متادیتای مقاله
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PUBLISHED, 
        verbose_name="Status"
    )
    reading_time = models.PositiveIntegerField(default=5, verbose_name="Reading Time (Minutes)")
    
    # نویسنده (با استفاده از تنظیمات استاندارد جنگو)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name="Author"
    )
    
    image = models.ImageField(upload_to='media/articles/images/', blank=True, null=True, verbose_name="Image")
    tags = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tags (Comma separated)")
    
    # سئو (SEO)
    seo_title = models.CharField(max_length=255, blank=True, null=True, verbose_name="SEO Title")
    description = models.TextField(blank=True, null=True, verbose_name="SEO Meta Description")
    
    # تاریخ‌ها
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-created_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # تولید خودکار اسلاگ یکتا
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)