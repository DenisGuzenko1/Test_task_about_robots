from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from robots.models import Robot


# Создаем функцию-обработчик, которая будет вызываться после сохранения объекта Robot
@receiver(post_save, sender=Robot)
def notify_user_if_robot_available(sender, instance, **kwargs):
    # Проверяем, доступен ли робот (quantity > 0 и is_available True)
    if instance.quantity > 0 and instance.is_available:
        # Получаем список заказов, связанных с этим роботом
        orders = instance.orders.all()
        # Для каждого заказа создаем и отправляем уведомление по электронной почте
        for order in orders:
            subject = "Робот доступен"
            message = (
                f"Добрый день!\n Недавно вы интересовались нашим роботом модели {instance.model}, "
                f"версии {instance.version}. \n Этот робот теперь в наличии. Если вам подходит "
                f"этот вариант - пожалуйста, свяжитесь с нами."
            )
            from_email = "gbublik2003@gmail.com"  # Отправитель письма
            recipient_list = [order.customer.email]  # Получатель письма

            # Отправляем письмо с указанными параметрами
            send_mail(subject, message, from_email, recipient_list)
