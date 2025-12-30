from django.contrib import admin
from .models import Product, Category, ProductImage
from reviews.models import Comments, Rating

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class RatingInline(admin.TabularInline):
    model = Rating
    fields = ['user', 'score']
    extra = 0
    readonly_fields = ['user', 'score']
    can_delete = False

class CommentsInline(admin.TabularInline):
    model = Comments
    fields = ['user', 'body', 'reply', 'is_reply', 'created']
    readonly_fields = ['user', 'body', 'reply', 'is_reply', 'created']
    extra = 0
    is_replay = False
    can_delete = True

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    raw_id_fields = ('category',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, CommentsInline, RatingInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
