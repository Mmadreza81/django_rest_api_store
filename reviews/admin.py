from django.contrib import admin
from .models import Comments, Rating

@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created', 'is_reply')
    raw_id_fields = ('user', 'product', 'reply')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'score']
    raw_id_fields = ['user', 'product']
