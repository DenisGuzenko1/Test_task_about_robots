from django.urls import path

from orders import views

urlpatterns = [
    path('', views.order, name='index'),
    path('success/', views.success, name='success')
]
