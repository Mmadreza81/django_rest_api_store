from rest_framework import serializers
from .models import User, Profile, Address, OtpCode


def clean_email(value):
    user = User.objects.filter(email=value).exists()
    if user:
        raise serializers.ValidationError('این ایمیل از قبل وجود دارد')
    # این خط رو حذف کنید! OtpCode در متد validate_email صدا زده میشه، نه در یک تابع خارجی
    # OtpCode.objects.filter(email=value).delete()
    return value


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'username', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
            # 👇 اصلاح شده: اعتبارسنجی ایمیل در متد validate_email انجام شود
            # 'email': {'validators': [clean_email]},
        }

    # --- متد validate برای تطابق پسوردها و حذف password2 ---
    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        # 1. چک کردن تطابق پسوردها (رفع مشکل data['key'] که باعث کرش QueryDict می‌شد)
        if password and password2 and password != password2:
            raise serializers.ValidationError({'password2': 'پسورد ها یکی نیستند!'})

        # 2. حذف password2 از داده‌های نهایی چون در مدل User وجود ندارد
        if 'password2' in data:
            del data['password2']

        return data

    # --- متد validate_field برای email (جایگزین تابع clean_email) ---
    def validate_email(self, value):
        # 1. چک کردن یونیک بودن ایمیل
        user = User.objects.filter(email=value).exists()
        if user:
            raise serializers.ValidationError('این ایمیل از قبل وجود دارد')

        # 2. حذف کدهای OTP قدیمی برای اطمینان از ارسال کد جدید
        OtpCode.objects.filter(email=value).delete()
        return value

    # --- متد validate_field برای username ---
    def validate_username(self, value):
        # ⚠️ اصلاح شده: در متدهای validate_field، 'value' خودش همان مقدار است
        # نیازی به value['username'] نیست.
        user = User.objects.filter(username=value).exists()
        if user:
            raise serializers.ValidationError('این نام کاربری از قبل وجود دارد')
        return value

    # --- متد validate_field برای phone_number ---
    def validate_phone_number(self, value):
        # ⚠️ اصلاح شده: نیازی به value['phone_number'] نیست.
        user = User.objects.filter(phone_number=value).exists()
        if user:
            raise serializers.ValidationError('این شماره تماس از قبل وجود دارد')
        return value

    def create(self, validated_data):
        # ساخت کاربر غیرفعال (فعالسازی پس از تایید OTP)
        # ⚠️ اصلاح شده: استفاده از create_user برای هندل کردن پسورد
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user


class OtpVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()


class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['age', 'image', 'image_url', 'full_name']
        extra_kwargs = {
            'image': {'write_only': True},
        }

    def get_image_url(self, obj):
        return obj.get_image_url()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']


class UserInfoSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)  # نام ریلیشن در مدل Address 'addresses' است

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone_number', 'profile', 'addresses']
