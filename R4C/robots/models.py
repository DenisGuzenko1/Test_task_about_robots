from django.db import models

from orders.models import Order


class Robot(models.Model):
    serial = models.CharField(max_length=5, blank=False, null=False)
    model = models.CharField(max_length=2, blank=False, null=False)
    version = models.CharField(max_length=2, blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False)
    quantity = models.PositiveIntegerField(null=True)
    is_available = models.BooleanField(default=True)
    orders = models.ManyToManyField(Order, blank=True)

    def __str__(self):
        return f'{self.model} {self.serial} {self.version}'
