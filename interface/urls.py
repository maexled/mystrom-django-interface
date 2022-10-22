from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('results/mystrom/<int:id>', views.mystrom_results, name='mystrom_results'),
    path('results/shelly/<int:id>', views.shelly_results, name='shelly_results'),
    path('results/maxcube/<int:id>', views.maxcube_results, name='maxcube_results'),
    path('devices/mystrom/<int:id>', views.mystrom_device_info, name='mystrom_device'),
    path('devices/mystrom', views.mystrom_devices, name='mystrom_devices'),
    path('devices/shelly/<int:id>', views.shelly_device_info, name='shelly_device'),
    path('devices/shelly', views.shelly_devices, name='shelly_devices'),
]