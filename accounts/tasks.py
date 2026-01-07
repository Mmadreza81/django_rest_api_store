from celery import shared_task
from accounts.models import OtpCode
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import pytz

@shared_task
def remove_expired_otp_codes():
    expired_time = timezone.now() - timedelta(minutes=2)
    deleted_count, _ = OtpCode.objects.filter(created_at__lt=expired_time).delete()
    if deleted_count > 0:
        print(f'---success: deleted {deleted_count} OTP codes---')
    print(f'deleted {deleted_count} expired OTP codes')

@shared_task
def send_otp_email_async(otp_id):
    try:
        otp = OtpCode.objects.get(pk=otp_id)
        tehran_timezone = pytz.timezone('Asia/Tehran')
        local_expire_tome = otp.expired_at.astimezone(tehran_timezone)
        readable_time = local_expire_tome.strftime('%H:%M:%S')

        subject = 'کد تایید ورود به فروشگاه'
        message = f"""
                سلام،
                کد تایید شما: {otp.code}
                این کد تا ساعت {readable_time} معتبر است.

                اگر شما این درخواست را نداده‌اید، این ایمیل را نادیده بگیرید.
                """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [otp.email],
            fail_silently=False,
        )
    except OtpCode.DoesNotExist:
        return 'otp code does not exist'
