from django.urls import path
from . import views

urlpatterns = [
    path('devices/', views.device_list, name='rest_device_index'),
    path('devices/<int:id>/', views.device_detail, name='rest_device_detail'),
]