from celery import shared_task
from accounts.models import OtpCode
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def remove_expired_otp_codes():
    expired_time = timezone.now() - timedelta(minutes=2)
    deleted_count, _ = OtpCode.objects.filter(created__lt=expired_time).delete()
    print(f'deleted {deleted_count} expired OTP codes')

@shared_task
def send_otp_email_async(otp_id):
    try:
        otp = OtpCode.objects.get(pk=otp_id)
    except OtpCode.DoesNotExist:
        return
    subject = f'OTP Verification for {otp.email}'
    message = f'Your OTP code: {otp.code}. It expired at {otp.expired_at}.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [otp.email])
