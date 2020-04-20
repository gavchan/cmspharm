from django import forms
from django.forms import ModelForm
from .models import DrugDelivery

class NewDrugDeliveryForm(ModelForm):
    expiry_date = forms.DateField(
        widget=forms.SelectDateWidget(
            empty_label=("Choose Year", "Choose Month", "Choose Day"),
        )
    )

    class Meta:
        model = DrugDelivery
        exclude = ['id']

