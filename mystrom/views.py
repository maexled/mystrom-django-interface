import json

from django.urls import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages

from mystrom_rest.models import MystromDevice, MystromResult
from .forms import MystromDeviceForm

def index(request):
    if request.method == "POST":
        form = MystromDeviceForm(request.POST)
        if form.is_valid():
            device = form.save()
            # want to return this device, but form.save() does not provied id
            # probably not the best solution
            return render(request, 'device_table_entry.html', {
                'device' : MystromDevice.objects.last()
            })
#            return HttpResponse(
#                status=204,
#                headers={
#                    'HX-Trigger': json.dumps({
#                        "movieListChanged": None,
#                        "showMessage": f"{device.name} added."
#                    })
#                })
    else:
        form = MystromDeviceForm()

    return render(request, 'index.html', {
        'devices' : MystromDevice.objects.all(),
        'form': form
    })

def delete_device(request, id):
    if request.method == "DELETE":
        pass
