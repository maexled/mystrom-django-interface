from django import forms
from mystrom_rest.models import MystromDevice
 
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
        ]