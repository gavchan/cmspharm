from django import forms
from django.forms import ModelForm
from .models import DrugDelivery

class NewDrugDeliveryForm(ModelForm):
    delivery_date = forms.DateField(
        widget=forms.SelectDateWidget(
            empty_label=("Choose Year", "Choose Month", "Choose Day"),
        )
    )
    expiry_date = forms.DateField(
        widget=forms.SelectDateWidget(
            empty_label=("Choose Year", "Choose Month", "Choose Day"),
        )
    )

    class Meta:
        model = DrugDelivery
        exclude = ['id']

class DrugDeliveryUpdateForm(ModelForm):
    delivery_date = forms.DateField(
        widget=forms.SelectDateWidget(
            empty_label=("Choose Year", "Choose Month", "Choose Day"),
        )
    )
    expiry_date = forms.DateField(
        widget=forms.SelectDateWidget(
            empty_label=("Choose Year", "Choose Month", "Choose Day"),
        )
    )

    class Meta:
        model = DrugDelivery
        exclude = ['id', 'product_name', 'registration_no']