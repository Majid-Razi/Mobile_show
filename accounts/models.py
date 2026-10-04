from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator
import uuid


class CustomUserManager(BaseUserManager):


    def create_user(self, email,phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        if not phone_number:
            raise ValueError('The Phone Number field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)


        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    #========Identification Fields========
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name='User ID')

    email = models.EmailField(
        unique=True,
        verbose_name='Email Address',
        error_messages={
            'unique': "A user with that email already exists.",
        })
    
    phone_number = models.CharField(
            max_length=11,
            unique=True,
            validators=[
                RegexValidator(
                    regex=r'^09\d{9}$',
                    message= " شماره موبایل باید با 09 شروع شود و 11 رقم باشد"
                ),
                MinLengthValidator(10)
            ],
            verbose_name='Phone Number',
            error_messages={
                'unique': "A user with that phone number already exists.",
                })

    
    #========Name Fields========
    full_name = models.CharField(
        max_length=150, 
        blank=True,
        verbose_name='نام کامل')
    
    first_name = models.CharField(
        max_length=30, 
        blank=True,
        verbose_name='نام')
    
    last_name = models.CharField(
        max_length=30, 
        blank=True,
        verbose_name='نام خانوادگی')

    #========Date Fields========
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='تاریخ عضویت')

    last_login = models.DateTimeField(
        blank=True ,
        null=True,
        verbose_name='آخرین ورود')
    
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ تولد')
    

    #========Status Fields========
    is_staff = models.BooleanField(
        default=False,
        verbose_name='کارمند')

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال')

    is_verified = models.BooleanField(
        default=False,
        verbose_name='تایید شده')

    is_blocked = models.BooleanField(
        default=False,
        verbose_name='مسدود شده')

#========Field security and management========
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد تلاش‌های ناموفق ورود')

    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='آخرین تلاش ناموفق ورود')

# ========other Fields========
    avatar = models.ImageField(
        upload_to='images/avatars/',
        blank=True,
        null=True,
        verbose_name='آواتار')
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='بیوگرافی')

    website = models.URLField(
        blank=True,
        null=True,
        verbose_name='وبسایت')
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='مکان')

#=========== system actions ==========
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد')

    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='تاریخ بروزرسانی')

    # ===== تنظیمات احراز هویت =====

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    class Meta:
        db_table = 'users'
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['-date_joined']),
        ]

    def __str__(self):
        return self.email


    def get_full_name(self):
        if self.full_name:
            return self.full_name   
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]

    def is_verified_user(self):
        """بررسی تأیید بودن کاربر"""
        return self.is_verified
    
    def increase_failed_attempts(self):
        """افزایش تعداد تلاش‌های ناموفق"""
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        
        # اگر ۵ بار تلاش ناموفق داشت، کاربر رو مسدود کن
        if self.failed_login_attempts >= 5:
            self.is_blocked = True
            self.save(update_fields=['failed_login_attempts', 'last_failed_login', 'is_blocked'])

    def reset_failed_attempts(self):
        """بازنشانی تعداد تلاش‌های ناموفق"""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.save(update_fields=['failed_login_attempts', 'last_failed_login', 'is_blocked']) 

        
