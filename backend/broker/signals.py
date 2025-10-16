from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from orders.models import Order, OrderItem
from carts.models import Cart
from .producer import send_to_kafka
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def handle_order_save(sender, instance, created, **kwargs):
    items_total = sum(item.price * item.quantity for item in instance.orderitem_set.all())
    message = {
        'event_type': 'order_created' if created else 'order_updated',
        'order_id': instance.id,
        'user': instance.user.username if instance.user else 'anon',
        'phone': instance.phone_number,
        'total_price': items_total,
        'timestamp': instance.created_at.isoformat() if hasattr(instance, 'created_at') else '',  # Добавь поле если нет
    }
    send_to_kafka(settings.KAFKA_TOPICS['orders'], message)
    logger.info(f"Order event sent for {instance.id}")

@receiver(post_delete, sender=Order)
def handle_order_delete(sender, instance, **kwargs):
    message = {'event_type': 'order_deleted', 'order_id': instance.id}
    send_to_kafka(settings.KAFKA_TOPICS['orders'], message)

@receiver(post_save, sender=Cart)
def handle_cart_save(sender, instance, created, **kwargs):
    message = {
        'event_type': 'cart_updated',
        'product_id': instance.product.id,
        'quantity': instance.quantity,
        'user': instance.user.username if instance.user else 'session:' + instance.session_key,
    }
    send_to_kafka(settings.KAFKA_TOPICS['carts'], message)

@receiver(post_delete, sender=Cart)
def handle_cart_delete(sender, instance, **kwargs):
    message = {'event_type': 'cart_removed', 'product_id': instance.product.id}
    send_to_kafka(settings.KAFKA_TOPICS['carts'], message)