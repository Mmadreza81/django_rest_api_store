from django.contrib import admin
from .models import Order, OrderItem, Coupon

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'updated_at', 'paid_at', 'get_address')
    list_filter = ('paid_at',)
    inlines = (OrderItemInline,)
    readonly_fields = ['phone_number']

    def get_address(self, obj):
        if obj.address:
            return f'{obj.address.address} - {obj.address.postal_code}'
        return '-'
    get_address.short_description = 'Address'

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    pass
