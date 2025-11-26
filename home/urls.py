from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'home'

router = DefaultRouter()
router.register(r'', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')
urlpatterns = [
    path('', include(router.urls)),
]
