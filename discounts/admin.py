from django.contrib import admin
from .models import Discount


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        'code', 
        'value_type', 
        'Value', 
        'status', 
        'expired_date', 
        'used_count', 
        'discount_cont', 
        'first_buying'
    )
    list_filter = ('status', 'value_type', 'first_buying')
    search_fields = ('code', 'description')
    autocomplete_fields = ['sppicific_product', 'spicific_customer']
    readonly_fields = ('used_count', 'created_date')
    
    fieldsets = (
        ("Basic Information", {
            'fields': ('code', 'description', 'value_type', 'Value', 'status')
        }),
        ("Limits & Conditions", {
            'fields': ('discount_cont', 'used_count', 'min_order_amount', 'max_usage', 'expired_date')
        }),
        ("Targeting (Optional)", {
            'fields': ('sppicific_product', 'spicific_customer', 'first_buying')
        }),
        ("Timestamps", {
            'fields': ('created_date',),
        }),
    )