from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions, generics
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from .models import User, OtpCode, Address, WishList
from home.models import Product
from .serializers import UserRegisterSerializer, OtpVerifySerializer, UserInfoSerializer, AddressSerializer, ProfileSerializer, WishlistSerializer
from .tasks import send_otp_email_async
from rest_framework.parsers import MultiPartParser, FormParser


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # ایجاد OTP
            otp = OtpCode.create_for_email(user.email)
            # فراخوانی تسک ناهمگام (Async)
            send_otp_email_async.delay(otp.id)

            return Response({'message': 'کاربر ساخته شد.ایمیل خود را برای احراز هویت چک کنید.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OtpVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            otp = OtpCode.objects.filter(email=email, code=code, is_used=False).first()

            if not otp:
                return Response({'error': 'Invalid code'}, status=400)

            if otp.is_expired():
                return Response({'error': 'Code expired'}, status=400)

            # فعال‌سازی کاربر
            user = get_object_or_404(User, email=email)
            user.is_active = True
            user.save()

            otp.mark_used()

            # تولید توکن JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'اکانت با موفقیت فعال شد'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        serializer = UserInfoSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        profile = request.user.profile
        if 'image' in request.data and profile.image:
            profile.image.delete(save=True)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        profile = request.user.profile
        if profile.image:
            profile.image.delete(save=True)
            return Response({"message": "profile's picture was deleted",
                             "image_url": profile.get_image_url()}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "there is no picture attached"}, status=status.HTTP_400_BAD_REQUEST)


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class WishlistToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = WishList.objects.get_or_create(user=request.user, product=product)
        if not created:
            wishlist_item.delete()
            return Response({'message': "از لیست علاقه مندی ها حذف شد."}, status=status.HTTP_200_OK)
        return Response({'message': 'به لیست علاقه مندی ها اضافه شد.'}, status=status.HTTP_201_CREATED)

class WishlistListView(generics.ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WishList.objects.filter(user=self.request.user)
