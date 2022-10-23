from django import forms
from mystrom_rest.models import MystromDevice
from shelly3em_rest.models import Shelly3EMDevice
 
# creating a form
class MystromDeviceForm(forms.ModelForm):
 
    # create meta class
    class Meta:
        # specify model to be used
        model = MystromDevice
 
        # specify fields to be used
        fields = [
            "name",
            "ip",
            "active"
        ]

class Shelly3EMDeviceForm(forms.ModelForm):
 
    # create meta class
    class Meta:
        # specify model to be used
        model = Shelly3EMDevice
 
        # specify fields to be used
        fields = [
            "name",
            "ip",
            "active"
        ]