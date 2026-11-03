from django.conf import settings
from django.db import models
from django.utils import timezone
from products.models import Product  # ارتباط با محصولات


class Discount(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        EXPIRED = 'expired', 'Expired'

    class ValueType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage (%)'
        FIXED = 'fixed', 'Fixed Amount'

    # اطلاعات پایه
    code = models.CharField(max_length=50, unique=True, verbose_name="Discount Code")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # نوع و مقدار
    value_type = models.CharField(
        max_length=20, 
        choices=ValueType.choices, 
        default=ValueType.PERCENTAGE, 
        verbose_name="Value Type"
    )
    Value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Value")
    
    # محدودیت‌ها
    discount_cont = models.PositiveIntegerField(default=0, verbose_name="Total Usage Limit")
    used_count = models.PositiveIntegerField(default=0, verbose_name="Used Count")
    min_order_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, 
        blank=True, null=True, verbose_name="Minimum Order Amount"
    )
    max_usage = models.PositiveIntegerField(default=1, verbose_name="Max Usage Per User")
    
    # هدف‌های خاص
    sppicific_product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='discounts', 
        verbose_name="Specific Product"
    )
    spicific_customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='customer_discounts', 
        verbose_name="Specific Customer"
    )
    first_buying = models.BooleanField(default=False, verbose_name="Is For First Buying Only")
    
    # زمان و وضعیت
    expired_date = models.DateTimeField(verbose_name="Expired Date")
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.ACTIVE, 
        verbose_name="Status"
    )
    
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")

    class Meta:
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.code} - {self.Value}{'%' if self.value_type == self.ValueType.PERCENTAGE else 'T'}"

    def is_valid(self):
        now = timezone.now()
        if self.expired_date < now:
            if self.status != self.Status.EXPIRED:
                self.status = self.Status.EXPIRED
                self.save(update_fields=['status'])
            return False
            
        if self.status != self.Status.ACTIVE:
            return False
            
        if self.discount_cont > 0 and self.used_count >= self.discount_cont:
            return False
            
        return True