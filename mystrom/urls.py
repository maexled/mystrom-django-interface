from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('devices/<int:id>/', views.device_info, name='device'),
    path('devices/', views.devices, name='devices'),
]