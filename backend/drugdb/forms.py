from django import forms
from django.forms import ModelForm
from .models import DrugDelivery

class NewDrugDeliveryForm(ModelForm):
    received_date = forms.DateField(
        widget=forms.SelectDateWidget(
            empty_label=("Choose Year", "Choose Month", "Choose Day"),
        )
    )
    expiry_date = forms.DateField(
        widget=forms.SelectDateWidget(
            empty_label=("Choose Year", "Choose Month", "Choose Day"),
        )
    )
    purchase_quantity = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': 0.5})
    )
    bonus_quantity = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': 0.5})
    )
    unit_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': 0.5})
    )
    items_per_purchase = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': 1})
    )

    class Meta:
        model = DrugDelivery
        exclude = ['id']

class DrugDeliveryUpdateForm(ModelForm):
    received_date = forms.DateField(
        widget=forms.SelectDateWidget(
            empty_label=("Choose Year", "Choose Month", "Choose Day"),
        )
    )
    expiry_date = forms.DateField(
        widget=forms.SelectDateWidget(
            empty_label=("Choose Year", "Choose Month", "Choose Day"),
        )
    )
    purchase_quantity = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': 0.5})
    )
    bonus_quantity = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': 0.5})
    )
    unit_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': 0.5})
    )
    items_per_purchase = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': 1})
    )

    class Meta:
        model = DrugDelivery
        exclude = ['id', 'product_name', 'reg_no']