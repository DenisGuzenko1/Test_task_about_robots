from django import forms

from robots.models import Robot
from .models import Order


class OrderForm(forms.ModelForm):
    robot_model = forms.ChoiceField(choices=[('', 'Выберите модель робота')] + [(model, model) for model in
                                                                                Robot.objects.values_list('model',
                                                                                                          flat=True).distinct()])
    robot_version = forms.ChoiceField(choices=[('', 'Выберите версию робота')] + [(version, version) for version in
                                                                                  Robot.objects.values_list('version',
                                                                                                            flat=True).distinct()])
    robot_serial = forms.ChoiceField(choices=[('', 'Выберите серийный номер')] + [(serial, serial) for serial in
                                                                                  Robot.objects.values_list('serial',
                                                                                                            flat=True).distinct()])

    class Meta:
        model = Order
        fields = ['robot_model', 'robot_version', 'robot_serial']
