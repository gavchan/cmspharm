from django import forms
from django.forms import ModelForm
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Vendor, Item, DeliveryOrder, DeliveryItem
from ledger.models import PaymentMethod
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout, Row, Column, Div, HTML, Submit, Button, Hidden,
    Field, Fieldset,
)
from crispy_forms.bootstrap import (
    FormActions,
    FieldWithButtons,
    StrictButton,
    UneditableField,
    )
from bootstrap_datepicker_plus import DatePickerInput
from bootstrap_modal_forms.forms import BSModalForm
from datetime import date

class NewCategoryForm(ModelForm):
    class Meta:
        model = Category
        exclude = ['id', 'version', 'active',]

class CategoryUpdateForm(ModelForm):
    class Meta:
        model = Category
        exclude = ['id', 'version',]

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

class NewDeliveryOrderForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.vendor_obj= kwargs.pop('vendor_obj', None)
        super(NewDeliveryOrderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False 
        self.helper.form_id = 'id-DeliveryOrderForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'inventory:NewDeliveryOrder')
        #self.initial['entry_date'] = date.today().strftime('%Y-%m-%d')
        today_date = date.today().strftime('%Y-%m-%d')
        self.initial['received_date'] = today_date
        self.initial['payment_method'] = PaymentMethod.objects.get(name='Cheque').pk
        self.initial['version'] = 1
        if self.vendor_obj:
            self.initial['vendor'] = self.vendor_obj.id
            self.initial['payee'] = self.vendor_obj.name
        self.helper.layout = Layout(
            Hidden('version', '1'),
            Row(
                Column(
                    FieldWithButtons('vendor', StrictButton('<i class="far fa-user-plus"></i>', id='add_vendor_button', css_class='btn-secondary')),
                    css_class='form-group col-md-8 mb-0'
                    ),
                Column('payee', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('invoice_no', css_class='form-group col-md-4 mb-0'),
                Column('invoice_date', css_class='form-group col-md-4 mb-0'),
                Column('received_date', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('amount', css_class='form-group col-md-4 mb-0'),
                Column('is_paid', css_class='form-group col-md-4 mb-0'),
                Column('payment_method', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('payment_ref', css_class='form-group col-md-4 mb-0'),
                Column('expected_date', css_class='form-group col-md-4 mb-0'),
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                css_class="form-row",            ),
            Row(
                Column(Field('remarks', css_class='form-group col-md-8 mb-0', rows="1")),
                css_class="form-row",            
            ),
            FormActions(
                Submit('submit', 'Submit'),
            ),
        )

    class Meta:
        model = DeliveryOrder
        exclude = ['id', 'version', 'date_created', 'last_updated',]
        widgets = {
                    'expected_date': DatePickerInput(
                        options={
                            "format": "YYYY-MM-DD",
                            "showClose": True,
                            "showClear": True,
                            "showTodayButton": True,
                        }
                    ),
                    'invoice_date': DatePickerInput(
                        options={
                            "format": "YYYY-MM-DD",
                            "showClose": True,
                            "showClear": True,
                            "showTodayButton": True,
                        }
                    ),
                }

class DeliveryOrderAddDrugModalForm(BSModalForm):

    def __init__(self, *args, **kwargs):
        # self.request = kwargs.pop('request', None)
        self.delivery_obj = kwargs.pop('delivery_obj', None)
        self.drug_obj = kwargs.pop('drug_obj', None)
        super(DeliveryOrderAddDrugModalForm, self).__init__(*args, **kwargs)
        if not self.delivery_obj:
            print("Error - no delivery object")
        if not self.drug_obj:
            print("Error - no drug object")
        # print(f"Modal form using {self.delivery_obj.id}, drug={self.drug_obj.reg_no}")
        
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = True 
        self.helper.form_id = 'id-DeliveryOrderAddDrugForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'inventory:DeliveryOrderDetail', args=(self.delivery_obj.id,)
            )
        self.initial['item.name'] = self.drug_obj.name
        self.initial['item.reg_drug'] = self.drug_obj.reg_no
        self.initial['version'] = 1
        
        self.helper.layout = Layout(
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                """)
            ),
        )

    class Meta:
        model = DeliveryItem
        exclude = ['id']

class DeliveryOrderUpdateForm(ModelForm):
    class Meta:
        model = DeliveryOrder
        exclude = ['id', 'version', 'date_created', 'last_updated',]