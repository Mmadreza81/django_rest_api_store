from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from datetime import timedelta
from .models import OtpCode
from .serializers import OTPRequestSerializer, OTPVerifySerializer
from .tasks import send_otp_email_async
from rest_framework_simplejwt.tokens import RefreshToken

class OTPRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            hour_ago = timezone.now() - timedelta(hours=1)
            recent = OtpCode.objects.filter(email=email, created_at__gte=hour_ago).count()
            if recent >= 5:
                return Response({"detail": "too many requests. try later"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            otp = OtpCode.create_for_email(email)
            send_otp_email_async.delay(otp.id)
            return Response({"detail": "email sent"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            try:
                otp = OtpCode.objects.filter(email=email, code=code).order_by('-created_at').first()
            except OtpCode.DoesNotExist:
                return Response({"detail": "invalid code"}, status=status.HTTP_400_BAD_REQUEST)
            if not otp:
                return Response({"detail": "invalid code"}, status=status.HTTP_400_BAD_REQUEST)
            if otp.is_used:
                return Response({"detail": "code already used"}, status=status.HTTP_400_BAD_REQUEST)
            if otp.is_expired():
                return Response({"detail": "code expired"}, status=status.HTTP_400_BAD_REQUEST)
            if otp.attempts >= 5:
                return Response({"detail": "too many attempts"}, status=status.HTTP_400_BAD_REQUEST)
            otp.mark_used()

            token = RefreshToken.for_user(otp.user) if otp.user else None
            return Response({"detail": "verified", "token": str(token.access_token) if token else None}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
