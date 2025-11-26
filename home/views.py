from rest_framework import viewsets, filters, permissions
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django.db.models import Avg

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]

    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Product.objects.all()
        queryset = queryset.annotate(annotated_avg_rating=Avg('prating__score'))
        queryset = queryset.prefetch_related('pcomments', 'prating')
        return queryset

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]

    queryset = Category.objects.filter(is_sub=False)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
