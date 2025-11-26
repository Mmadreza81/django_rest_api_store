from rest_framework import viewsets, permissions
from .models import Comments, Rating
from .serializers import CommentSerializer, RatingSerializer
from permissions import IsOwnerOrReadOnly

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Comments.objects.all()
        queryset = queryset.filter(reply__isnull=True)
        queryset = queryset.select_related('user', 'reply', 'reply__user')
        queryset = queryset.order_by('-created')
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Rating.objects.all()

    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        user = self.request.user
        existing_rating = Rating.objects.filter(product_id=product_id, user=user).first()
        if existing_rating:
            serializer.instance = existing_rating
            serializer.save()
        else:
            serializer.save(user=user)
