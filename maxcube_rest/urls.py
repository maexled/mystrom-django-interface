from django.urls import path
from . import views

urlpatterns = [
    path('devices/', views.device_list, name='maxcube_rest_device_index'),
    path('devices/<int:id>/', views.device_detail, name='maxcube_rest_device_detail'),
    path('devices/<int:id>/results/', views.device_results, name='maxcube_rest_device_results'),
]