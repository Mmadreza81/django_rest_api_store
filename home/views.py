from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions
from .models import Product, Category
from .filters import ProductFilter
from .serializers import ProductSerializer, CategorySerializer
from django.db.models import Avg, Q
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]

    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['price', 'created']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = (Product.objects.filter(available=True).
                    annotate(annotated_avg_rating=Avg('prating__score')).
                    prefetch_related('pcomments', 'prating', 'images'))
        search_text = self.request.query_params.get('search', None)
        if search_text:
            vector = (SearchVector('name', weight='A', config='simple') +
                      SearchVector('description', weight='B', config='simple'))
            query = SearchQuery(search_text, config='simple')
            queryset = (queryset.annotate(rank=SearchRank(vector, query),
                                          similarity=TrigramSimilarity('name', search_text)).
                        filter(Q(rank__gte=0.3) | Q(similarity__gte=0.1)).order_by('-rank', '-similarity'))
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        return queryset

    @action(detail=True, methods=['get'])
    def related_products(self, request, slug=None):
        product = self.get_object()
        categories = product.category.all()
        related = Product.objects.filter(category__in=categories,
                                         available=True).exclude(id=product.id).distinct().order_by('?')[:4]

        serializer = self.get_serializer(related, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]

    queryset = Category.objects.filter(is_sub=False)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
