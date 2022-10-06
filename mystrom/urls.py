from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.results, name='results'),
    path('results/mystrom/<int:id>', views.mystrom_results, name='mystrom_results'),
    path('results/shelly/<int:id>', views.shelly_results, name='shelly_results'),
    path('devices/<int:id>/', views.device_info, name='device'),
    path('devices/', views.devices, name='devices'),
]