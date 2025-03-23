from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.get(id=order_id)
        send_mail(
            subject='Подтверждение заказа',
            message=f'Ваш заказ #{order.id} принят. Спасибо за покупку!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
        )
    except Order.DoesNotExist:
        pass

@shared_task
def send_admin_notification_email(order_id):
    try:
        order = Order.objects.get(id=order_id)
        send_mail(
            subject='Новый заказ',
            message=f'Заказ #{order.id} от {order.customer.username}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )
    except Order.DoesNotExist:
        pass
