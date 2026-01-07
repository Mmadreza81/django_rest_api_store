from rest_framework import serializers
from .models import Order, OrderItem, CartItem, Cart
from home.serializers import ProductSerializer
from utils import to_jalali


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSerializer.Meta.model
        fields = ['id', 'name', 'price', 'slug']

# سریالایزر مخصوص نمایش اقلام داخل  Cart
class CartItemModelSerializer(serializers.ModelSerializer):
    product_detail = SimpleProductSerializer(source='product', read_only=True)
    formatted_line_total = serializers.SerializerMethodField()
    formatted_unit_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'formatted_unit_price', 'formatted_line_total']
        read_only_fields = ['cart', 'formatted_line_total']

    def get_formatted_unit_price(self, obj):
        return "{:,}".format(int(obj.product.price))

    def get_formatted_line_total(self, obj):
        return "{:,}".format(int(obj.line_total))

class CartSerializer(serializers.ModelSerializer):
    items = CartItemModelSerializer(many=True, read_only=True)
    formatted_total_price = serializers.SerializerMethodField()
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    jalali_updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'formatted_total_price', 'coupon', 'coupon_code']

    def get_formatted_total_price(self, obj):
        return "{:,}".format(int(obj.get_total_price()))

    def get_jalali_updated_at(self, obj):
        return to_jalali(obj.updated_at)

class OrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    formatted_line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_detail', 'unit_price', 'quantity', 'formatted_line_total']

    def get_formatted_line_total(self, obj):
        return "{:,}".format(int(obj.line_total))


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address_detail = serializers.SerializerMethodField()
    formatted_price = serializers.SerializerMethodField()
    jalali_created_at = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at',
                  'discount', 'items', 'formatted_price', 'paid_at',
                  'phone_number', 'address_detail', 'jalali_created_at']
        read_only_fields = ['user', 'paid_at', 'status', 'discount']

    def get_address_detail(self, obj):
        if obj.address:
            return {'city': obj.address.city,
                    'address': obj.address.address,
                    'postal_code': obj.address.postal_code}
        return None

    def get_formatted_price(self, obj):
        return "{:,}".format(int(obj.get_total_price()))

    def get_jalali_created_at(self, obj):
        return to_jalali(obj.created_at)
