from django.urls import path
from . import views

urlpatterns = [
    path('devices/', views.device_list, name='shelly_rest_device_index'),
    path('devices/<int:id>/', views.device_detail, name='shelly_rest_device_detail'),
    path('devices/<int:id>/results/', views.device_results, name='shelly_rest_device_results'),
]