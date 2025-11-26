from django.db import models
from accounts.models import User
from home.models import Product

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ucomments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='pcomments')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, related_name='rcomments', null=True, blank=True)
    is_reply = models.BooleanField(default=False)
    body = models.TextField(max_length=400)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.body[:30]}'

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='urating')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prating')
    score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.product.name} ({self.score})'
