from django.db import models
from accounts.models import User
from django.conf import settings

class Category(models.Model):
    name= models.CharField(max_length=150, unique=True)
    image= models.ImageField(upload_to='images/category/')
    # icon= models.
    is_active= models.BooleanField(default=True)
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
    
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ["name"]

        