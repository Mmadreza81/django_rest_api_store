from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order

@receiver(pre_save, sender=Order)
def update_product_stock(sender, instance, **kwargs):
    if not instance.pk:
        return
    old_order = Order.objects.get(pk=instance.pk)
    if not old_order.paid and instance.paid:
        for item in instance.items.all():
            product = item.product
            if product.stock >= item.quantity:
                product.stock -= item.quantity
                product.save()
            else:
                raise ValueError(f'موجودی محصول {product.name} کافی نیست!')
