from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=20, verbose_name='Имя')
    surname = models.CharField(max_length=20, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')

    def __str__(self):
        return f"{self.name} {self.surname}"
