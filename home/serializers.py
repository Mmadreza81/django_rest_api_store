from rest_framework import serializers
from .models import Category, Product, ProductImage
from reviews.serializers import RatingReadOnlySerializer, CommentReadOnlySerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'is_sub', 'sub_category']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField(many=True)
    rating = RatingReadOnlySerializer(many=True, read_only=True, source='prating')
    rating_avg = serializers.SerializerMethodField()
    comments = CommentReadOnlySerializer(many=True, read_only=True, source='pcomments')

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'stock',
                  'available', 'rating_avg', 'rating', 'category', 'images', 'comments']

    def get_rating_avg(self, obj):
        if hasattr(obj, 'annotated_avg_rating') and obj.annotated_avg_rating is not None:
            return round(obj.annotated_avg_rating, 2)
        return 0.0
