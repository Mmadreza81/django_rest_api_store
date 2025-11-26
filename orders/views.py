from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from django.db.models import F
from django.db import transaction
import requests
import json
from accounts.models import Address

# ایمپورت مدل‌ها و سریالایزرها
from .models import Order, OrderItem, Cart, CartItem, Coupon
from home.models import Product
from .serializers import CartSerializer, OrderSerializer

# --- پیکربندی زرین‌پال ---
# فرض می‌شود تنظیمات زیر در settings.py شما تعریف شده است
if settings.SANDBOX:
    ZP_API_REQUEST = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
    ZP_API_VERIFY = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
    ZP_API_STARTPAY = "https://sandbox.zarinpal.com/pg/StartPay/{authority}"
else:
    ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
    ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
    ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"


# -----------------------------------------------------------
# ۱. مدیریت سبد خرید (CartAPIView)
# -----------------------------------------------------------

class CartAPIView(APIView):
    """مدیریت سبد خرید مبتنی بر مدل (Model-Based)"""
    permission_classes = [permissions.IsAuthenticated]

    # GET: نمایش محتویات سبد خرید
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    # POST: افزودن/ویرایش آیتم
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id or quantity <= 0:
            return Response({'error': 'Invalid product_id or quantity'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        # اگر کاربر قبلاً سبد خرید نداشته باشد، ایجاد می‌شود
        cart, created = Cart.objects.get_or_create(user=request.user)

        # بازیابی یا ایجاد آیتم سبد خرید و افزایش تعداد
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not item_created:
            # اگر آیتم از قبل موجود بود، فقط تعداد را اضافه می‌کنیم
            cart_item.quantity = F('quantity') + quantity
            cart_item.save()
            cart_item.refresh_from_db()  # برای خواندن مقدار جدید

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE: حذف آیتم یا پاکسازی سبد
    def delete(self, request):
        product_id = request.data.get('product_id')

        cart = get_object_or_404(Cart, user=request.user)

        if product_id:
            # حذف یک آیتم خاص
            item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
            item.delete()
            message = 'Item removed from cart'
        else:
            # پاکسازی کامل سبد خرید
            cart.items.all().delete()
            cart.coupon = None
            cart.save()
            message = 'Cart cleared'

        serializer = CartSerializer(cart)
        return Response({'message': message, 'cart': serializer.data}, status=status.HTTP_200_OK)


# -----------------------------------------------------------
#۲. اعمال کد تخفیف (ApplyCouponView)
# -----------------------------------------------------------

class ApplyCouponView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        cart = get_object_or_404(Cart, user=request.user)

        if not code:
            # اگر کد خالی بود، کوپن اعمال شده را حذف می‌کنیم
            cart.coupon = None
            cart.save()
            serializer = CartSerializer(cart)
            return Response({'message': 'Coupon removed', 'discount': 0, 'cart': serializer.data},
                            status=status.HTTP_200_OK)

        try:
            now = timezone.now()
            coupon = Coupon.objects.get(
                code__iexact=code,
                valid_from__lte=now,
                valid_to__gte=now,
                active=True
            )
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid or expired coupon code'}, status=status.HTTP_404_NOT_FOUND)

        cart.coupon = coupon
        cart.save()

        serializer = CartSerializer(cart)

        return Response({
            'message': 'Coupon applied successfully',
            'discount': coupon.discount,
            'cart': serializer.data
        }, status=status.HTTP_200_OK)


# -----------------------------------------------------------
#۳. ایجاد سفارش (OrderCreateView)
# -----------------------------------------------------------

class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        # 1. بازیابی سبد خرید مبتنی بر مدل
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # 2. دریافت تخفیف
        discount = cart.coupon.discount if cart.coupon else 0

        user_address = None
        try:
            user_address = request.user.addresses
        except AttributeError:
            user_address = None
        except Address.DoesNotExist:
            user_address = None

        if not user_address:
            return Response({'error': 'please select or create a shipping address.'}, status=status.HTTP_400_BAD_REQUEST)
        pass

        user_phone = request.user.phone_number if hasattr(request.user, 'phone_number') else None

        # 3. ایجاد سفارش نهایی
        order = Order.objects.create(user=request.user, discount=discount, address=user_address, phone_number=user_phone)

        # 4. انتقال اقلام و پاکسازی سبد خرید
        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                unit_price=item.product.price,
                quantity=item.quantity
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)  # ایجاد سریعتر اقلام سفارش

        cart_items.delete()  # حذف اقلام سبد خرید
        cart.coupon = None
        cart.save()

        serializer = OrderSerializer(order)

        return Response({
            'message': 'Order created successfully. Proceed to payment.',
            'order_detail': serializer.data
        }, status=status.HTTP_201_CREATED)


# -----------------------------------------------------------
# # ۴. پرداخت (OrderPayView & VerifyPaymentView)
# -----------------------------------------------------------

class OrderPayView(APIView):
    """شروع فرایند پرداخت و اتصال به زرین‌پال"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user, status='Pending')

        # بررسی آدرس کاربر
        # فرض بر این است که آدرس از طریق OneToOneField به User متصل است (یا هر مکان دیگری که شما تعریف کرده‌اید)
        if hasattr(request.user, 'addresses') and request.user.addresses:
            order.address = request.user.addresses
            order.phone_number = request.user.phone_number  # اگر شماره تلفن را در آدرس ذخیره کرده‌اید
            order.save()
        else:
            return Response({'error': 'Please set your address in profile first.'}, status=status.HTTP_400_BAD_REQUEST)

        amount = int(order.get_total_price())  # تبدیل به ریال (یا تومان بسته به تنظیمات زرین‌پال)
        description = f"Order #{order.id} Payment"
        callback_url_with_id = f'{settings.CALLBACKURL}?order_id={order.id}'

        data = {
            "merchant_id": settings.MERCHANT,
            "amount": amount,
            "description": description,
            "callback_url": callback_url_with_id,
            "metadata": {"mobile": request.user.phone_number or '', "email": request.user.email or ''}
        }

        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        try:
            res = requests.post(ZP_API_REQUEST, data=json.dumps(data), headers=headers, timeout=10)
            res_data = res.json()
            if res.status_code == 200 and res_data['data']['code'] == 100:
                authority = res_data['data']['authority']
                return Response({
                    'payment_url': ZP_API_STARTPAY.format(authority=authority),
                    'authority': authority
                })
            return Response({'error': 'Zarinpal Error', 'detail': res_data}, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({'error': 'Connection Error', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyPaymentView(APIView):
    permission_classes = [permissions.AllowAny]

    """بررسی و تأیید نهایی پرداخت توسط زرین‌پال"""

    # 💡 توجه: این View معمولاً احراز هویت JWT را ندارد و نیاز به روش دیگری برای تشخیص کاربر دارد
    # (مثلاً ارسال یک پارامتر user_id در callback_url)

    def get(self, request):
        authority = request.GET.get('Authority')
        status_pay = request.GET.get('Status')
        order_id = request.GET.get('order_id')

        if status_pay != 'OK':
            return Response({'error': 'Payment Canceled'}, status=status.HTTP_400_BAD_REQUEST)

        # ⬅️ نکته: یافتن آخرین سفارش معلق کاربر در اینجا ممکن است ریسکی باشد.
        # بهتر است Order ID را از طریق metadata یا callback URL دریافت کنید.
        # اما در حال حاضر فرض می‌کنیم request.user معتبر است و از last() استفاده می‌کنیم.

        if not order_id:
            return Response({'error': 'No pending order found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            order = get_object_or_404(Order, id=order_id, status='Pending')
        except ValueError:
            return Response({'error': 'invalid order id format'}, status=status.HTTP_400_BAD_REQUEST)

        amount = int(order.get_total_price())  # تبدیل واحد قیمت

        data = {
            "merchant_id": settings.MERCHANT,
            "amount": amount,
            "authority": authority
        }
        headers = {'content-type': 'application/json', 'accept': 'application/json'}

        res = requests.post(ZP_API_VERIFY, data=json.dumps(data), headers=headers)
        res_data = res.json()

        if res.status_code == 200 and res_data['data']['code'] == 100:
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.save()

            return Response({'message': 'Payment successful', 'ref_id': res_data['data']['ref_id']})

        return Response({'error': 'Payment verification failed', 'detail': res_data},
                        status=status.HTTP_400_BAD_REQUEST)
