from rest_framework import serializers
from home.models import Product
from .models import Comments, Rating
from utils import to_jalali


class RecursiveCommentSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = CommentSerializer(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    replied_to_user = serializers.SerializerMethodField()
    replies = RecursiveCommentSerializer(many=True, read_only=True, source='rcomments')
    reply = serializers.PrimaryKeyRelatedField(queryset=Comments.objects.all(), required=False, allow_null=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)
    jalali_updated = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = ['id', 'user', 'product', 'reply', 'replies', 'is_reply', 'body', 'jalali_updated', 'replied_to_user']
        read_only_fields = ['user']

    def get_replied_to_user(self, obj):
        if obj.reply:
            return obj.reply.user.username
        return None

    def get_jalali_updated(self, obj):
        return to_jalali(obj.updated)

class CommentReadOnlySerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comments
        fields = ['id', 'user', 'body', 'created']
        read_only_fields = fields


class RatingReadOnlySerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'user', 'score']
        read_only_fields = fields


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'product', 'score']
