# Generated by Django 4.2.5 on 2023-09-30 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_customer_notification_sent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='notification_sent',
        ),
    ]
