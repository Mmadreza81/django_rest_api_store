from django.contrib import admin
from .models import Order, OrderItem, Coupon
from jalali_date.admin import ModelAdminJalaliMixin
from utils import to_jalali


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)


@admin.register(Order)
class OrderAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'get_total_price', 'get_paid_at_shamsi', 'get_address')
    ordering = ('-paid_at',)
    list_filter = ('status', ('paid_at', admin.DateFieldListFilter))
    inlines = (OrderItemInline,)
    readonly_fields = ['phone_number']

    def get_address(self, obj):
        if obj.address:
            return f'{obj.address.address} - {obj.address.postal_code}'
        return '-'

    @admin.display(description='تاریخ ثبت ', ordering='paid_at')
    def get_paid_at_shamsi(self, obj):
        return to_jalali(obj.created_at)

    get_address.short_description = 'Address'


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    pass
