from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'accounts'

router = DefaultRouter()
router.register(r'addresses', views.AddressViewSet, basename='address')

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify/', views.VerifyOtpView.as_view(), name='verify_otp'),
    path('resend/', views.ResendOtpView.as_view(), name='resend_otp'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('wishlist/', views.WishlistListView.as_view(), name='wishlist-list'),
    path('wishlist/toggle/<int:product_id>/', views.WishlistToggleView.as_view(), name='wishlist-toggle'),
    path('', include(router.urls)),
]
