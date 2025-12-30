from rest_framework import serializers
from .models import Category, Product, ProductImage
from reviews.serializers import RatingReadOnlySerializer, CommentReadOnlySerializer
from accounts.models import WishList


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'is_sub', 'sub_category']

class ProductImageSerializer(serializers.ModelSerializer):
    # image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['image']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return "https://api-shop.s3.ir-thr-at1.arvanstorage.ir/default/default_product.png"

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    category = serializers.StringRelatedField(many=True)
    rating = RatingReadOnlySerializer(many=True, read_only=True, source='prating')
    rating_avg = serializers.SerializerMethodField()
    comments = CommentReadOnlySerializer(many=True, read_only=True, source='pcomments')
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'stock',
                  'available', 'rating_avg', 'rating', 'category', 'images', 'comments', 'is_favorite']

    def get_images(self, obj):
        images_queryset = obj.images.all()
        if images_queryset.exists():
            return ProductImageSerializer(images_queryset, many=True, context=self.context).data
        return [{'image': "https://api-shop.s3.ir-thr-at1.arvanstorage.ir/default/default_product.png"}]

    def get_rating_avg(self, obj):
        if hasattr(obj, 'annotated_avg_rating') and obj.annotated_avg_rating is not None:
            return round(obj.annotated_avg_rating, 2)
        return 0.0

    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return WishList.objects.filter(user=user, product=obj).exists()
        return False
