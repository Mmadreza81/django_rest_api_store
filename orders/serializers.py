from rest_framework import serializers
from .models import Order, OrderItem, CartItem, Cart
from home.serializers import ProductSerializer


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSerializer.Meta.model
        fields = ['id', 'name', 'price', 'slug']

# سریالایزر مخصوص نمایش اقلام داخل Session Cart
class CartItemModelSerializer(serializers.ModelSerializer):
    product_detail = SimpleProductSerializer(source='product', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'line_total']
        read_only_fields = ['cart', 'line_total']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemModelSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField(source='get_total_price')
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'coupon', 'coupon_code']

class OrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_detail', 'unit_price', 'quantity', 'line_total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField(source='get_total_price')
    address_detail = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at',
                  'discount', 'items', 'total_price', 'paid_at', 'phone_number', 'address_detail']
        read_only_fields = ['user', 'paid_at', 'status', 'discount']

    def get_address_detail(self, obj):
        if obj.address:
            return {'city': obj.address.city,
                    'address': obj.address.address,
                    'postal_code': obj.address.postal_code}
        return None
