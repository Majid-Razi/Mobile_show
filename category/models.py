from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, allow_unicode=True, blank=True)
    image = models.ImageField(upload_to='images/category/', null=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='children'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    @property
    def product_count(self):
        return self.products.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f'{self.parent.name} → {self.name}'
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'owner'],
                name='unique_category_per_owner'
            ),
            models.UniqueConstraint(
                fields=['slug', 'owner'],
                name='unique_category_slug_per_owner'
            ),
        ]
        indexes = [
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['owner', 'is_active']),
        ]