from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.results, name='results'),
    path('devices/<int:id>/', views.device_info, name='device'),
    path('devices/', views.devices, name='devices'),
]