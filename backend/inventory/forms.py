from django import forms
from django.forms import ModelForm
from django.urls import reverse
from .models import Category, Vendor, Item, ItemDelivery
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout, Row, Column, Div, HTML, Submit, Button, Hidden,
    Field, Fieldset,
)
from crispy_forms.bootstrap import (
    FormActions,
    FieldWithButtons,
    StrictButton,
    )
from bootstrap_modal_forms.forms import BSModalForm

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

class NewVendorModalForm(BSModalForm):

    def __init__(self, *args, **kwargs):
        super(NewVendorModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-NewVendorModalForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'inventory:NewVendorModal')
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-4 mb-0'),
                Column('alias', css_class='form-group col-md-4 mb-0'),
                Column('account_no', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('default_exp_category', css_class="col-md-4 mb-0"),
                Column('default_description', css_class="col-md-4 mb-0"),
                Column('contact_person', css_class='form-group col-md-4 mb-0'),
                css_class='form-row,'
            ),
            Row(
                Column(Field('remarks', rows='3'), css_class='form-group col-md-4 mb-0'),
                Column(Field('address', rows='3'), css_class='form-group col-md-4 mb-0'),
                Column('email', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('tel_main', css_class='form-group col-md-4 mb-0'),
                Column('tel_mobile', css_class='form-group col-md-4 mb-0'),
                Column('tel_office', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('fax', css_class='form-group col-md-4 mb-0'),
                Column('website', css_class='form-group col-md-4 mb-0'),
                Column(Field('active'), Field('is_supplier'), css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                """),
            ),
        )

    class Meta:
        model = Vendor
        exclude = ['id', 'version', 'date_created', 'last_updated',]

class NewVendorForm(ModelForm):
    class Meta:
        model = Vendor
        exclude = ['id', 'version', 'date_created', 'last_updated',]

class VendorUpdateForm(ModelForm):
    class Meta:
        model = Vendor
        exclude = ['id', 'version', 'date_created', 'last_updated',]

class VendorUpdateModalForm(BSModalForm):

    def __init__(self, *args, **kwargs):
        super(VendorUpdateModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-VendorUpdateModalForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'inventory:VendorUpdateModal', args=(self.instance.pk,))
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-4 mb-0'),
                Column('alias', css_class='form-group col-md-4 mb-0'),
                Column('account_no', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('default_exp_category', css_class="col-md-4 mb-0"),
                Column('default_description', css_class="col-md-4 mb-0"),
                Column('contact_person', css_class='form-group col-md-4 mb-0'),
                css_class='form-row,'
            ),
            Row(
                Column(Field('remarks', rows='3'), css_class='form-group col-md-4 mb-0'),
                Column(Field('address', rows='3'), css_class='form-group col-md-4 mb-0'),
                Column('email', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('tel_main', css_class='form-group col-md-4 mb-0'),
                Column('tel_mobile', css_class='form-group col-md-4 mb-0'),
                Column('tel_office', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('fax', css_class='form-group col-md-4 mb-0'),
                Column('website', css_class='form-group col-md-4 mb-0'),
                Column(Field('active'), Field('is_supplier'), css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                """),
            ),
        )

    class Meta:
        model = Vendor
        exclude = ['id', 'version', 'date_created', 'last_updated',]
