from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for the User model.
    """

    #=======نمایش لیست کاربران در پنل ادمین========
    list_display = [
        'email',
        'phone_number',
        'full_name',
        'show_avatar',
        'is_active',
        'is_verified',
        'is_blocked',
        'is_staff',
        'date_joined',
        'last_login',
        'failed_login_attempts_display',
    ]

    # ===== فیلترهای سمت راست =====

    list_filter = [
        'is_active',
        'is_staff',
        'is_superuser',
        'is_verified',
        'is_blocked',
        'date_joined',
        'is_verified',
    ]


    #========فیلدهای جستجو========
    search_fields = [
        'email',
        'phone_number',
        'first_name',
        'last_name',
        'full_name',
        'id',
    ]

    #==========ترتیب پیش فرض نمایش کاربران========
    ordering = ['-date_joined'] 


    # ===== فیلدهای قابل ویرایش مستقیم در لیست =====
    list_editable = [
        'is_active',
        'is_verified',
        'is_blocked',
        'is_staff',
    ]
    
    # ===== اکشن‌های سفارشی =====
    actions = [
        'make_verified',
        'make_unverified',
        'block_users',
        'unblock_users',
        'activate_users',
        'deactivate_users',
    ]
    
    # ===== بخش‌بندی فرم ویرایش =====
    fieldsets = (
        # بخش اول: اطلاعات اصلی
        (_('اطلاعات اصلی'), {
            'fields': (
                'email',
                'phone_number',
                'password',
            )
        }),
        
        # بخش دوم: اطلاعات شخصی
        (_('اطلاعات شخصی'), {
            'fields': (
                'full_name',
                'first_name',
                'last_name',
                'birth_date',
                'avatar',
                'bio',
                'website',
                'location',
            )
        }),
        
        # بخش سوم: وضعیت کاربر
        (_('وضعیت کاربر'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'is_verified',
                'is_blocked',
            )
        }),
        
        # بخش چهارم: امنیت
        (_('امنیت و ورود'), {
            'fields': (
                'failed_login_attempts',
                'last_failed_login',
                'last_login',
            )
        }),
        
        # بخش پنجم: تاریخ‌ها (قابل جمع شدن)
        (_('تاریخ‌های سیستمی'), {
            'fields': (
                'date_joined',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    # ===== فیلدهای فقط خواندنی =====
    readonly_fields = [
        'date_joined',
        'created_at',
        'updated_at',
        'last_login',
        'failed_login_attempts',
        'last_failed_login',
        'show_avatar_preview',
    ]
    
    # ===== فرم ایجاد کاربر جدید =====
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'phone_number',
                'full_name',
                'password1',
                'password2',
            ),
        }),
    )

    #========تنظیمات پیشرفته========
    save_on_top = True  # نمایش دکمه‌های ذخیره در بالای فرم
    show_full_result_count = True  # نمایش تعداد کل نتایج در بالای لیست 


    #=======متد های نمایش سفارشی=========
    @admin.display(description='تصویر پروفایل', ordering='avatar')
    def show_avatar(self, obj):
        """
        نمایش تصویر پروفایل کاربر در لیست کاربران.
        """
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.avatar.url
            )
        return format_html(
            '<span style="display: inline-block; width: 40px; height: 40px; '
            'background: #6c757d; border-radius: 50%; color: white; '
            'text-align: center; line-height: 40px; font-weight: bold;">{}</span>',
            obj.get_short_name()[0].upper() if obj.get_short_name() else '?'
        )
    show_avatar.short_description = 'آواتار'


    @admin.display(description='تلاش‌های ناموفق', ordering='failed_login_attempts')
    def failed_login_attempts_display(self, obj):
        """نمایش تعداد تلاش‌های ناموفق با رنگ‌بندی"""
        if obj.failed_login_attempts >= 5:
            color = 'red'
        elif obj.failed_login_attempts >= 3:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.failed_login_attempts
        )
    
    @admin.display(description='پیش‌نمایش آواتار')
    def show_avatar_preview(self, obj):
        """نمایش آواتار در فرم ویرایش"""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="150" height="150" style="border-radius: 10px; object-fit: cover;" />',
                obj.avatar.url
            )
        return "آواتاری ثبت نشده است"

    
    # ===== اکشن‌های سفارشی =====
    
    @admin.action(description='تأیید کاربران انتخاب شده')
    def make_verified(self, request, queryset):
        """تأیید کاربران"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} کاربر تأیید شدند.')
    
    @admin.action(description='لغو تأیید کاربران انتخاب شده')
    def make_unverified(self, request, queryset):
        """لغو تأیید کاربران"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} کاربر لغو تأیید شدند.')
    
    @admin.action(description='مسدود کردن کاربران انتخاب شده')
    def block_users(self, request, queryset):
        """مسدود کردن کاربران"""
        updated = queryset.update(is_blocked=True)
        self.message_user(request, f'{updated} کاربر مسدود شدند.')
    
    @admin.action(description='رفع مسدودیت کاربران انتخاب شده')
    def unblock_users(self, request, queryset):
        """رفع مسدودیت کاربران"""
        updated = queryset.update(is_blocked=False, failed_login_attempts=0)
        self.message_user(request, f'{updated} کاربر رفع مسدودیت شدند.')
    
    @admin.action(description='فعال کردن کاربران انتخاب شده')
    def activate_users(self, request, queryset):
        """فعال کردن کاربران"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} کاربر فعال شدند.')
    
    @admin.action(description='غیرفعال کردن کاربران انتخاب شده')
    def deactivate_users(self, request, queryset):
        """غیرفعال کردن کاربران"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} کاربر غیرفعال شدند.')
    
    # ===== ذخیره‌سازی =====
    def save_model(self, request, obj, form, change):
        """
        عملیات قبل از ذخیره‌سازی
        """
        # اگر کاربر جدید است و رمز عبور ست شده
        if not change and obj.password:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)
    
    # ===== دسترسی‌ها =====
    def get_queryset(self, request):
        """
        فیلتر کردن کوئری‌ست بر اساس دسترسی
        """
        qs = super().get_queryset(request)
        # اگر سوپرادمین نیست، فقط کاربران عادی رو ببین
        if not request.user.is_superuser:
            qs = qs.filter(is_superuser=False)
        return qs
    
    def has_delete_permission(self, request, obj=None):
        """
        فقط سوپرادمین می‌تونه حذف کنه
        """
        if obj and obj.is_superuser:
            return request.user.is_superuser
        return super().has_delete_permission(request, obj)


        