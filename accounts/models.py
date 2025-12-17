from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import UserManager
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=200, unique=True)
    phone_number = models.CharField(max_length=11, unique=True)
    username = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'username']

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin

def validate_image_size(file):
    file_size = file.size
    if file_size > 4 * 1024 * 1024:
        raise ValidationError("image size must be less than 4MB")

def user_directory_path(instance, filename):
    return f'profile_pic/{instance.user.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True, validators=[validate_image_size])
    full_name = models.CharField(max_length=200, null=True, blank=True)

    def get_image_url(self):
        if self.image:
            return self.image.url
        return "https://api-shop.s3.ir-thr-at1.arvanstorage.ir/default/default.png"

    def __str__(self):
        if self.full_name:
            return self.full_name
        return self.user.username

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address = models.TextField()
    city = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=25)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.address} - {self.postal_code}'

class OtpCode(models.Model):
    email = models.EmailField(db_index=True)
    code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['email', 'code']),
            models.Index(fields=['email', 'created_at']),
        ]

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=['is_used'])

    def is_expired(self):
        return timezone.now() >= self.expired_at

    @classmethod
    def create_for_email(cls, email, ttl_minutes=5, code=None):
        if code is None:
            import secrets
            code = f'{secrets.randbelow(10**6):06d}'
        expired_at = timezone.now() + timedelta(minutes=ttl_minutes)
        return cls.objects.create(email=email, code=code, expired_at=expired_at)

    def __str__(self):
        return f'{self.email} - {self.code} - {self.created_at}'
