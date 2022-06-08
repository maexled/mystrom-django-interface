import json

from django.urls import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from mystrom_rest.models import MystromDevice, MystromResult
from .forms import MystromDeviceForm

def index(request):
    form = MystromDeviceForm()

    return render(request, 'index.html', {
        'devices' : MystromDevice.objects.all(),
        'form': form
    })

def devices(request):
    if request.method == "POST":
        form = MystromDeviceForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'device_table_entries.html', {
                'devices' : MystromDevice.objects.all(),
            })
        else:
            return render(request, 'device_form_rows.html', {
                'form' : form,
            })
    elif request.method == "DELETE":
        MystromDevice.objects.all().delete()
        return render(request, 'device_table_entries.html', {
            'devices' : []
        })
    else:
        form = MystromDeviceForm()
    return render(request, 'device_form.html', {
        'form': form
    })

def device_info(request, id):
    device = get_object_or_404(MystromDevice, id=id)
    if request.method == "POST":
        form = MystromDeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            return render(request, 'device_table_entries.html', {
                'devices' : MystromDevice.objects.all(),
            })
        else:
             return render(request, 'device_form_rows.html', {
                'form' : form,
            })
    elif request.method == "DELETE":
        MystromDevice.objects.filter(id=device.id).delete()
        return render(request, 'device_table_entries.html', {
            'devices' : MystromDevice.objects.all(),
        })
    else:
        form = MystromDeviceForm(instance=device)
    return render(request, 'device_form.html', {
        'form': form,
        'device': device,
    })