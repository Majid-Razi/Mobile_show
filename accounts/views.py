from django.conf import settings
from rest_framework.generics import CreateAPIView, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .models import User
from .serializers import UserSerializer,LoginSerializer, UserRegisterationSerializer

# class RegisterView(CreateAPIView):
    # serializer_class = UserSerializer
    # permission_classes = [AllowAny]

    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data =request.data)
    #     serializer.is_valid(raise_exception=True)

    #     user = serializer.save()
    #     # password = serializer.validated_data.get("password")
    #     # user.set_password(password)
    #     # user.save()

    #     refresh = RefreshToken.for_user(user)
    #     access_token = str(refresh.access_token)
    #     refresh_token = str(refresh)


    #     response = Response({
    #         "message": "Login is success and you login.",
    #         "access": access_token,
    #         "refresh": refresh_token ,
    #         "user": UserSerializer(user).data
    #     }, status=status.HTTP_201_CREATED)

    #     # ست کردن کوکی
    #     data = {
    #         "access": access_token,
    #         "refresh": refresh_token,
    #     }

    #     response.set_cookie(
    #         key="access_token",
    #         value=access,
    #         httponly=True,
    #         secure=True,
    #         samesite="None",
    #         max_age=60 * 20, )

    #     response.set_cookie(
    #         key="refresh_token",
    #         value=refresh_token,
    #         httponly=True,
    #         secure=True,
    #         samesite="None",
    #         max_age=20 * 24 * 60 * 60, )

    #     return response

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response(
            {
                "message": "User registered successfully.",
                "access": access_token,
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )

        # در لوکال: secure=False, samesite='Lax'
        # در پروداکشن: secure=True, samesite='None'
        cookie_secure = not settings.DEBUG
        cookie_samesite = "None" if not settings.DEBUG else "Lax"

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=cookie_secure,
            samesite=cookie_samesite,
            max_age=60 * 20,
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=cookie_secure,
            samesite=cookie_samesite,
            max_age=20 * 24 * 60 * 60,
        )

        return response


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']   # ← این خط جایگزین شد

        # user = authenticate(request, username=username, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials")


        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {

            "message": "User logged in successfully.",
            "refresh": str(refresh),
            "access": access,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
            }
             }, status.HTTP_200_OK)

        data = {
            "access": access,
            "refresh": refresh_token,
        }

        response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=60 * 20, )

        response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=20 * 24 * 60 * 60, )

        return response

        # refresh = RefreshToken.for_user(user)
        # access_token = str(refresh.access_token)
        # # refresh_token = str(refresh)

        # response = Response(
        #     {
        #         "message": "User logged in successfully.",
        #         "access": access_token,
        #         "refresh": str(refresh),
        #         "user": UserSerializer(user).data,
        #     },
        #     status=status.HTTP_200_OK,
        # )

        # # در لوکال: secure=False, samesite='Lax'
        # # در پروداکشن: secure=True, samesite='None'
        # cookie_secure = not settings.DEBUG
        # cookie_samesite = "None" if not settings.DEBUG else "Lax"

        # response.set_cookie(
        #         key="access_token",
        #         value=access_token,
        #         httponly=True,
        #         secure=cookie_secure,
        #         samesite=cookie_samesite,
        #         max_age=60 * 20,
        #     )
        # response.set_cookie(
        #         key="refresh_token",
        #         value=str(refresh),
        #         httponly=True,
        #         secure=cookie_secure,
        #         samesite=cookie_samesite,
        #         max_age=20 * 24 * 60 * 60,
        # )

        # return response
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # ۱) چک کردن پر بودن فیلدها
        if not email or not password:
            raise ValidationError({
                "detail": "ایمیل و رمز عبور الزامی است"
            })

        # ۲) پیدا کردن کاربر با ایمیل
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("ایمیل یا رمز عبور اشتباه است")

        # ۳) چک کردن رمز عبور
        if not user.check_password(password):
            raise AuthenticationFailed("ایمیل یا رمز عبور اشتباه است")

        # ۴) اطمینان از اینکه کاربر لاگین‌شده همون کاربریه که ایمیلش رو وارد کرده
        if user.id != request.user.id:
            raise AuthenticationFailed("ایمیل وارد شده با کاربر لاگین‌شده مطابقت ندارد")

        # ۵) blacklist کردن توکن و پاک کردن کوکی‌ها
        refresh_token = (
            request.COOKIES.get("refresh_token")
            or request.data.get("refresh_token")
        )

        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass

        response = Response(
            {"message": "Successfully logged out!"},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("access_token", samesite="None")
        response.delete_cookie("refresh_token", samesite="None")
        return response

# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]   # ← حالا درست کار می‌کنه

#     def post(self, request):
#         refresh_token = (
#             request.COOKIES.get("refresh_token")
#             or request.data.get("refresh_token")
#         )

#         if refresh_token:
#             try:
#                 RefreshToken(refresh_token).blacklist()
#             except TokenError:
#                 pass   # حتی اگه نامعتبر بود، بازم کوکی‌ها رو پاک کن

#         response = Response(
#             {"message": "Successfully logged out!"},
#             status=status.HTTP_200_OK,
#         )
#         response.delete_cookie("access_token", samesite="None")
#         response.delete_cookie("refresh_token", samesite="None")
#         return response

        
class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        #if not found refresh_token
        if not refresh_token:
            return Response({"detail": "No refresh token provided"}, status=status.HTTP_400_BAD_REQUEST)
            # اینجا باید منطق صدور access جدید باشه
            
        try:
            refresh =RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            response = Response({"access": access_token}, status=status.HTTP_200_OK)
            response.set_cookie(key="access_token",
                            value=access_token,
                            httponly=True,
                            secure=True,
                            samesite="None")
            return response
        
        except InvalidToken:
            return  Response({"error": "Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED)