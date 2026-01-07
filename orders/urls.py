from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    # مدیریت سبد خرید (GET, POST, DELETE)
    # GET: نمایش محتویات سبد خرید
    # POST: افزودن آیتم به سبد خرید
    # DELETE: حذف یک آیتم یا پاکسازی کامل سبد خرید
    path('cart/', views.CartAPIView.as_view(), name='cart-management'),

    # اعمال کوپن تخفیف
    path('coupon/apply/', views.ApplyCouponView.as_view(), name='apply-coupon'),

    # ایجاد سفارش نهایی
    path('create/', views.OrderCreateView.as_view(), name='order-create'),

    # شروع فرایند پرداخت (نیاز به order ID)
    # POST: شروع ارتباط با درگاه پرداخت
    path('<int:pk>/pay/', views.OrderPayView.as_view(), name='order-pay'),

    # تأیید نهایی پرداخت (Callback URL)
    # GET: دریافت پاسخ از زرین‌پال و تأیید نهایی
    path('verify/', views.VerifyPaymentView.as_view(), name='order-verify'),
    path('my-orders/', views.UserOrdersListView.as_view(), name='user-orders-list'),
    path('my-orders/<int:id>/', views.UserOrderDetailView.as_view(), name='user-orders-detail'),
]
