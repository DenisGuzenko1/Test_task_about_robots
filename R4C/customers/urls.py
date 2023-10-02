from django.urls import path

from customers import views

urlpatterns = [
    path('', views.index, name='index'),
]
