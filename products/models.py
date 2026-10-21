from django.db import models
from django.utils.text import slugify
from category.models import Category
from django.conf import settings 

class Product(models.Model):
    # ارتباط با دسته‌بندی (اگر دسته‌بندی حذف شود، محصولاتش پاک نشوند بلکه فیلدشان خالی شود)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products',
        verbose_name="Category"
    )
    
    # اطلاعات پایه محصول
    name = models.CharField(max_length=255, unique=True, verbose_name="Product Name")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    
    # قیمت و انبارداری
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Price")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock Count")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    
    # توضیحات و تصاویر
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Main Image")
    
    # ارتباط با کاربر سازنده (مشابه کتگوری)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='products',
        verbose_name="Owner"
    )
    
    # تاریخ‌ها
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_date'] # جدیدترین‌ها در ابتدا

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # تولید خودکار اسلاگ از روی نام اگر خالی باشد
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)