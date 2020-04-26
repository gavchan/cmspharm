from django import forms
from django.forms import ModelForm
from .models import Category, Vendor, Item, ItemDelivery

class NewCategoryForm(ModelForm):
    class Meta:
        model = Category
        exclude = ['id', 'version', 'active',]

class CategoryUpdateForm(ModelForm):
    class Meta:
        model = Category
        exclude = ['id', 'version',]

class NewItemDeliveryForm(ModelForm):
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
        widget=forms.NumberInput(attrs={'step': 0.1})
    )
    items_per_purchase = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': 1})
    )

    class Meta:
        model = ItemDelivery
        exclude = ['id',]

class ItemDeliveryUpdateForm(ModelForm):
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
        widget=forms.NumberInput(attrs={'step': 0.1})
    )
    items_per_purchase = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': 1})
    )

    class Meta:
        model = ItemDelivery
        exclude = ['id', 'product_name',]

class NewItemForm(ModelForm):
    class Meta:
        model = Item
        exclude = ['id', 'version', 'date_created',]

class ItemUpdateForm(ModelForm):
    class Meta:
        model = Item
        exclude = ['id', 'version', 'date_created',]

class NewVendorForm(ModelForm):
    class Meta:
        model = Vendor
        exclude = ['id', 'version', 'date_created', 'last_updated',]

class VendorUpdateForm(ModelForm):
    class Meta:
        model = Vendor
        exclude = ['id', 'version', 'date_created', 'last_updated',]

