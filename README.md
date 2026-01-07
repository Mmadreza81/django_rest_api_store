# 🛒 Advanced Django E-commerce API

یک اکوسیستم فروشگاهی کامل و حرفه‌ای پیاده‌سازی شده با Django Rest Framework. این پروژه تمام نیازهای یک فروشگاه مدرن از مدیریت موجودی تا سیستم‌های تعامل با کاربر و پرداخت را پوشش می‌دهد.

---

## 🌟 قابلیت‌های کلیدی (Core Features)

### 🔐 امنیت و احراز هویت
* JWT Authentication: استفاده از JSON Web Tokens برای مدیریت نشست‌های کاربر به صورت Stateless و امن.
* OTP Login: ورود امن با ایمیل و کد یکبار مصرف.
* Smart Resend Logic: محدودیت ۳۰ ثانیه‌ای برای درخواست مجدد کد جهت جلوگیری از سوءاستفاده.
* Auto-Cleanup: حذف خودکار کدهای منقضی شده توسط Celery.

### 🛍 محصولات و فروش
* Advanced Search & Filtering: سیستم فیلترینگ پیشرفته محصولات بر اساس دسته‌بندی، قیمت و ویژگی‌ها.
* High-Performance Cart: سبد خرید مبتنی بر Redis برای تجربه کاربری سریع و بدون لگ.
* Order Flow: تبدیل سبد خرید به سفارش قطعی و ارسال فاکتور رسمی به ایمیل کاربر.

### 💬 تعامل و بازخورد (User Engagement)
* Nested Comments: سیستم کامنت‌گذاری تودرتو (Tree Structure) برای پرسش و پاسخ و نقد محصولات.
* Star Rating: سیستم امتیازدهی دقیق کاربران به محصولات.

### 🇮🇷 بومی‌سازی (Localization)
* Jalali Calendar: نمایش تمام تاریخ‌های سفارشات، محصولات و نظرات به صورت شمسی.
* Persian Admin: فیلترهای زمانی محلی.

---

## 🛠 تکنولوژی‌ها و مدیریت سرویس‌ها

| تکنولوژی | کاربرد |
| :--- | :--- |
| Django / DRF | موتور اصلی پروژه و APIها |
| SimpleJWT | مدیریت توکن‌های JWT برای احراز هویت |
| Redis | مدیریت سبد خرید و Message Broker |
| Celery | مدیریت تسک‌های سنگین (ارسال ایمیل و نظافت دیتابیس) |
| NSSM (Windows) | مدیریت و اجرای پایداری Redis و Celery به عنوان ویندوز سرویس |

---

## ⚙️ پایداری در محیط ویندوز (Service Management)

برای تضمین پایداری پروژه در محیط ویندوز، از ابزار NSSM (Non-Sucking Service Manager) استفاده شده است. تمامی سرویس‌های زیر به صورت Windows Service تنظیم شده‌اند تا در صورت ریستارت شدن سرور، به صورت خودکار اجرا شوند:
- Redis Server
- Celery Worker
- Celery Beat (جهت تسک‌های زمان‌بندی شده)

---

## 🚀 راه اندازی سریع

۱. نصب نیازمندی‌ها:
   `bash
   pip install -r requirements.txt

   python manage.py migrations

   python manage.py migrate

   python manage.py runserver