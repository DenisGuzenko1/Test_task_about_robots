"""R4C URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from robots.views import export_to_excel
from robots import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('orders.urls'), name='index'),  # главная страница, для заказа роботов
    path('api/robots/', views.robot_list, name='robot-list'),  # API с информацией по роботам
    path('export-to-excel/', export_to_excel, name='export-to-excel'),  # ссылка для создания Excel-файла
]
