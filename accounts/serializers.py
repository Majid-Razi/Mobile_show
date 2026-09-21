from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
             سریالایزر برای نمایش اطلاعات کاربر
             استفاده در: نمایش پروفایل، لیست کاربران
    """
     
    class Meta:
        model = User

        fields = [
            'id',             
            'email', 
            'phone_number', 
            'full_name',
            'first_name', 
            'last_name', 
            'avatar', 
            'bio',
            'website', 
            'location',
            'date_joined', 
            'is_verified',
            'is_blocked',
        ]

        read_only_fields = [
             'id', 
            'email', 
            'phone_number', 
            'date_joined', 
            'is_verified',
            'is_blocked'
        ]


# ==========================================
# ۴. سریالایزر ثبت نام کاربر جدید
# ==========================================
class UserRegisterationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        error_messages={
            'required': 'رمز عبور الزامی است',
            'blank': 'رمز عبور نمی‌تواند خالی باشد',
        }
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        error_messages={
            'required': 'تکرار رمز عبور الزامی است',
            'blank': 'تکرار رمز عبور نمی‌تواند خالی باشد',
        }
    )

    class Meta:
        model = User          # ✅ حروف کوچک
        fields = [
            "email",
            "full_name",
            # "first_name",
            # "last_name",
            "avatar",
            "bio",
            "website",
            "phone_number",
            "password",
            "password2",
        ]

        extra_kwargs = {
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'ایمیل الزامی است',
                    'invalid': 'فرمت ایمیل نامعتبر است',
                }
            },
            'phone_number': {
                'required': True,
                'error_messages': {
                    'required': 'شماره موبایل الزامی است',
                }
            },
            'full_name': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email already exist.")
        return value

    def validate_phone_number(self, value):
        import re
        if not re.match(r'^09\d{9}$', value):
            raise serializers.ValidationError(
                "شماره موبایل باید با 09 شروع شود و 11 رقم باشد"
            )
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone_number already exist.")
        return value

    def validate(self, attrs):
        """
        اعتبارسنجی تطابق رمز عبور
        """
        if attrs['password'] != attrs['password2']:   # ✅ رشته، نه self.password
            raise serializers.ValidationError({
                'password': 'رمزهای عبور مطابقت ندارند',
                'password2': 'رمزهای عبور مطابقت ندارند',
            })
        return attrs

    def create(self, validated_data):
        """
        create new user
        """
        # حذف password2 از داده‌ها
        validated_data.pop('password2')   # ✅ رشته، نه self.password2

        # ایجاد کاربر با استفاده از CustomUserManager
        user = User.objects.create_user(**validated_data)
        return user


    
# ==========================================
# ۵. سریالایزر لاگین 
# ==========================================
class LoginSerializer(serializers.Serializer):



    """
    سریالایزر برای ورود کاربر
    """

    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "وارد کردن ایمیل الزامی است",
            "invalid": "فرمت ایمیل نامعتبر است",
        }
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        error_messages={
            "required": "وارد کردن رمز عبور الزامی است"
        }
    )

    def validate(self, attrs):
        """
        اعتبارسنجی اطلاعات ورود
        """
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'کاربری با این ایمیل یافت نشد'
            })

        # بررسی مسدود بودن کاربر
        if user.is_blocked:
            raise serializers.ValidationError({
                'email': 'این کاربر مسدود شده است. با پشتیبانی تماس بگیرید.'
            })

        # بررسی فعال بودن کاربر
        if not user.is_active:
            raise serializers.ValidationError({
                'email': 'این کاربر غیرفعال است.'
            })

        # بررسی رمز عبور
        if not user.check_password(password):
            user.increase_failed_attempts()
            raise serializers.ValidationError({
                'password': 'رمز عبور اشتباه است'
            })

        # بازنشانی تلاش‌های ناموفق در صورت ورود موفق
        if user.failed_login_attempts > 0:
            user.reset_failed_attempts()

        # ✅ قرار دادن کاربر در attrs (نه context)
        attrs['user'] = user

        return attrs

# ==========================================
# ۴. سریالایزر تغییر رمز عبور
# ==========================================

class ChangePasswordSerializer(serializers.Serializer):
    """
    سریالایزر برای تغییر رمز عبور

    """

    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'رمز عبور فعلی الزامی است',
        }
    )


    new_password = serializers.CharField(
        write_only = True,
        required = True,
        style = {"input_type":"password"},
        error_messages ={
            "required" : "رمز جدید الزامی است"
        }
    )

    new_password2 = serializers.CharField(
        write_only = True,
        required = True,
        style = {"input_type":"password"},
        error_messages =
        {
            "required" : "تکرار رمز جدید الزامی است"
        }
    )

    def validate_old_password(self, value):
        """
        اعتبارسنجی رمز عبور فعلی
        """

        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("رمز عبور فعلی اشتباه است")
        return value


    def validate(self, attrs):
        """
        اعتبارسنجی تطابق رمز عبور جدید

        """

        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"new_password": "رمز های عبور جدید مطابقت ندارند"}
            )
        return attrs
        
    def save(self, **kwargs):
        """
        ذخیره رمز عبور جدید

        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user




class ResetPasswordSerializer(serializers.Serializer):
    """
    سریالایزر برای بازنشانی رمز عبور
    """
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'},
        error_messages={
            'required': 'وارد کردن رمز جدید الزامی است.',
            'blank': 'رمز جدید نمی‌تواند خالی باشد.',
            'min_length': 'رمز جدید باید حداقل ۸ کاراکتر باشد.',
        }
    )

    new_password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'تکرار رمز عبور جدید الزامی است',
        }
    )

    def validate_new_password(self, value):
        # اعتبارسنجی قدرت رمز با قوانین Django
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {'new_password': 'رمزهای عبور مطابقت ندارند'}
            )
        return attrs

    def save(self, user):
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user



# ۲. سریالایزر درخواست بازنشانی (فراموشی)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'ایمیل الزامی است',
            'invalid': 'ایمیل معتبر نیست',
        }
    )


# ==========================================
# ۹. سریالایزر آپلود آواتار
# ==========================================

class AvatarUploadSerializer(serializers.Serializer):
    """
    سریالایزر برای آپلود و بروزرسانی آواتار

    """

    class Meta:
        model = User
        fields = ['avatar']
        extra_kwargs = {
            'avatar': {
                'required': True,
                'error_messages': {
                    'required': 'فایل آواتار الزامی است',
                    'invalid': 'فرمت فایل نامعتبر است',
                }
            }
        }


    def validate_avatar(self, value):
        """
        اعتبارسنجی فایل آواتار
        """
        # بررسی حجم (حداکثر ۲ مگابایت)
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("حجم فایل نباید بیشتر از ۲ مگابایت باشد")
        
        # بررسی فرمت
        allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError(
                "فرمت فایل باید یکی از JPEF, PNG, GIF, WEBP باشد"
            )
        
        return value