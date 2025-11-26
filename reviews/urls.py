from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reviews'

router = DefaultRouter()
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'ratings', views.RatingViewSet, basename='rating')
urlpatterns = [
    path('', include(router.urls)),
]
