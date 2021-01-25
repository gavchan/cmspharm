from django import forms
from django.forms import ModelForm
from django.urls import reverse
# from django.utils import timezone
from datetime import datetime

from django.contrib.auth.models import User
from .models import Category, Vendor, Item, DeliveryOrder, DeliveryItem, ItemType
from cmsinv.models import InventoryItem
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
# from datetime import date

class NewCategoryForm(ModelForm):
    class Meta:
        model = Category
        exclude = ['id', 'version', 'active',]

class CategoryUpdateForm(ModelForm):
    class Meta:
        model = Category
        exclude = ['id', 'version',]


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
            Hidden('next', self.helper.form_action),
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
    
    def __init__(self, *args, **kwargs):
        self.next_url = kwargs.pop('next_url')
        super(NewVendorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-NewVendorForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        if self.next_url:
            url_with_query = "%s?next=%s" % (
                reverse('inventory:NewVendor'), self.next_url
            )
        else:
            url_with_query = reverse('inventory:NewVendor')
        self.helper.form_action = url_with_query
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
                Button(
                    'back', 'Cancel',
                    css_class='btn-light',
                    onclick="javascript:history.go(-1);"
                ),
            ),
        )

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

    received_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    invoice_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    due_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'})
        )
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
        #self.initial['entry_date'] = datetime.today().strftime('%Y-%m-%d')
        today_date = datetime.today().strftime('%Y-%m-%d')
        self.initial['received_date'] = today_date
        self.initial['payment_method'] = PaymentMethod.objects.get(name='Cheque').pk
        self.initial['version'] = 1
        if self.vendor_obj:
            self.initial['vendor'] = self.vendor_obj.id
            self.initial['payee'] = self.vendor_obj.name
        self.helper.layout = Layout(
            Hidden('version', '1'),
            Hidden('is_paid', False),
            Row(
                Column(
                    'vendor',
                    # FieldWithButtons('vendor', StrictButton('<i class="far fa-user-plus"></i>', id='add_vendor_button', css_class='btn-secondary')),
                    css_class='form-group col-md-8 mb-0'
                    ),
                # Column('received_date', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="received_date">Received date</label>
                    <div class="input-group date" id="datepicker_received_date" data-target-input="nearest">
                        <input type="text" 
                            id="id_received_date"
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_received_date"
                            placeholder="YYYY-MM-DD"
                            name="received_date"
                        >
                        <div class="input-group-append" data-target="#datepicker_received_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                css_class='form-row',
            ),
            Row(
                Column('invoice_no', css_class='form-group col-md-8 mb-0'),
                # Column('invoice_date', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="invoice_date">Invoice date</label>*
                    <div class="input-group date" id="datepicker_invoice_date" data-target-input="nearest">
                        <input type="text"
                            id="id_invoice_date"
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_invoice_date"
                            placeholder="YYYY-MM-DD"
                            name="invoice_date"
                        >
                        <div class="input-group-append" data-target="#datepicker_invoice_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                css_class='form-row',
            ),
            Row(
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                Column('amount', css_class='form-group col-md-4 mb-0'),
                # Column('due_date', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="due_date">Due date</label>
                    <div class="input-group date" id="datepicker_due_date" data-target-input="nearest">
                        <input type="text"
                            id="id_due_date"
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_due_date"
                            placeholder="YYYY-MM-DD"
                            name="due_date"
                        >
                        <div class="input-group-append" data-target="#datepicker_due_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                css_class='form-row',
            ),
            Row(
                Column(Field('remarks', css_class='form-group col-md-12 mb-0', rows="2")),
                css_class="form-row",            
            ),
            FormActions(
                HTML("""
                <button type="button" class="btn btn-warning" id="btn_set_received">
                    Received=Invoice
                </button>
                <button class="btn btn-warning" type="button" id="btn_due1m">
                    Due=+1m
                </button>
                        """),
                Submit('submit', 'Submit'),
                Button(
                    'back', 'Cancel',
                    css_class='btn-light',
                    onclick="javascript:history.go(-1);"
                ),
            ),
        )

    class Meta:
        model = DeliveryOrder
        exclude = ['id', 'version', 'date_created', 'last_updated',]
        
class NewDeliveryOrderModalForm(BSModalForm):
    received_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    invoice_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    due_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'})
        )
    def __init__(self, *args, **kwargs):
        self.vendor_obj= kwargs.pop('vendor_obj', None)
        super(NewDeliveryOrderModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False 
        self.helper.form_id = 'id-DeliveryOrderForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'inventory:NewDeliveryOrderModal')
        #self.initial['entry_date'] = datetime.today().strftime('%Y-%m-%d')
        today_date = datetime.today().strftime('%Y-%m-%d')
        self.initial['received_date'] = today_date
        self.initial['payment_method'] = PaymentMethod.objects.get(name='Cheque').pk
        self.initial['version'] = 1
        if self.vendor_obj:
            self.initial['vendor'] = self.vendor_obj.id
            self.initial['payee'] = self.vendor_obj.name
        self.helper.layout = Layout(
            Hidden('next', self.helper.form_action),
            Hidden('version', '1'),
            Hidden('is_paid', False),
            Row(
                Column(
                    'vendor',
                    # FieldWithButtons('vendor', StrictButton('<i class="far fa-user-plus"></i>', id='add_vendor_button', css_class='btn-secondary')),
                    css_class='form-group col-md-8 mb-0'
                    ),
                # Column('received_date', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="received_date">Received date</label>
                    <div class="input-group date" id="datepicker_received_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_received_date"
                            placeholder="YYYY-MM-DD"
                            name="received_date"
                            id="id_received_date"
                        >
                        <div class="input-group-append" data-target="#datepicker_received_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                css_class='form-row',
            ),
            Row(
                Column('invoice_no', css_class='form-group col-md-8 mb-0'),
                # Column('invoice_date', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="invoice_date">Invoice date</label>*
                    <div class="input-group date" id="datepicker_invoice_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_invoice_date"
                            placeholder="YYYY-MM-DD"
                            name="invoice_date"
                            id="id_invoice_date"
                        >
                        <div class="input-group-append" data-target="#datepicker_invoice_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                css_class='form-row',
            ),
            Row(
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                Column('amount', css_class='form-group col-md-4 mb-0'),
                # Column('due_date', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="due_date">Due date</label>
                    <div class="input-group date" id="datepicker_due_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_due_date"
                            placeholder="YYYY-MM-DD"
                            name="due_date"
                            id="id_due_date"
                        >
                        <div class="input-group-append" data-target="#datepicker_due_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                css_class='form-row',
            ),
            Row(
                Column(Field('remarks', css_class='form-group col-md-12 mb-0', rows="2")),
                css_class="form-row",            
            ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                """),
            ),
        )

    class Meta:
        model = DeliveryOrder
        exclude = ['id', 'version', 'date_created', 'last_updated',]

class DeliveryOrderUpdateModalForm(BSModalForm):
    
    received_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    invoice_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    due_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'})
        )
    
    def __init__(self, *args, **kwargs):
        super(DeliveryOrderUpdateModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-DeliveryOrderUpdateForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'inventory:DeliveryOrderUpdateModal', args=(self.instance.pk,))
        self.helper.layout = Layout(
            Row(
                Column(
                    UneditableField('vendor'),
                    css_class='form-group col-md-8 mb-0'
                    ),
                # Column('received_date', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="received_date">Received date</label>
                    <div class="input-group date" id="datepicker_received_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_received_date"
                            placeholder="YYYY-MM-DD"
                            name="received_date"
                            id="id_received_date"
                            value="{{ deliveryorder_obj.received_date|date:'Y-m-d' }}"
                        >
                        <div class="input-group-append" data-target="#datepicker_received_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                css_class='form-row',
            ),
            Row(
                Column('invoice_no', css_class='form-group col-md-8 mb-0'),
                # Column('invoice_date', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="invoice_date">Invoice date</label>*
                    <div class="input-group date" id="datepicker_invoice_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_invoice_date"
                            placeholder="YYYY-MM-DD"
                            name="invoice_date"
                            id="id_invoice_date"
                            value="{{ deliveryorder_obj.invoice_date|date:'Y-m-d' }}"
                        >
                        <div class="input-group-append" data-target="#datepicker_invoice_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                css_class='form-row',
            ),
            Row(
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                Column('amount', css_class='form-group col-md-4 mb-0'),
                # Column('due_date', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="due_date">Due date</label>
                    <div class="input-group date" id="datepicker_due_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_due_date"
                            placeholder="YYYY-MM-DD"
                            name="due_date"
                            id="id_due_date"
                            value="{{ deliveryorder_obj.due_date|date:'Y-m-d' }}"
                        >
                        <div class="input-group-append" data-target="#datepicker_due_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
            ),
            Row(
                Column(Field('remarks', css_class='form-group col-md-12 mb-0', rows="2")),
                css_class="form-row",            
            ),
            Hidden('vendor', self.instance.vendor.pk),
            Hidden('version', self.instance.version + 1),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                """),
            ),
        )

    class Meta:
        model = DeliveryOrder
        exclude = ['id', 'items', 'is_paid', 'bill', 'date_created', 'last_updated',]

class DeliveryItemUpdateModalForm(BSModalForm):

    expiry_month = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYYMM'}))
    
    def __init__(self, *args, **kwargs):
        self.delivery_obj = kwargs.pop('delivery_obj', None)
        super(DeliveryItemUpdateModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-DeliveryOrderDeliveryItemUpdateForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'inventory:DeliveryItemUpdateModal', 
            kwargs={
                'delivery_id': self.delivery_obj.id,
                'pk': self.instance.pk,
            }
            )
        self.helper.layout = Layout(
            Hidden('item', self.instance.item.pk),
            Hidden('delivery_order', self.delivery_obj.id),
            Hidden('version', '1'),
            Row(
                Column(
                    Row(
                        Column('purchase_quantity',css_class='col-md-6 mb-0'),
                        Column('bonus_quantity', css_class='col-md-6 mb-0'),
                    ),
                    css_class="form-group col-md-4",
                ),
                Column(
                    Row(
                        Column('unit_price', css_class='col-md-6 mb-0'),
                        Column('discount', css_class='col-md-6 mb-0'),
                    ),
                    css_class="form-group col-md-4"
                ),
                Column('purchase_unit', css_class="form-group col-md-2"),
                Column('is_sample', css_class="form-group col-md-2"),
                css_class='form-row',
            ),
            Row(
                Column(
                    Row(
                        Column('items_per_purchase', css_class='col-md-6 mb-0'),
                        Column('items_unit', css_class='col-md-6 mb-0'),
                    ),
                    css_class="form-group col-md-4"
                ),
                Column(
                    Row(
                        Column('batch_num', css_class='col-md-6 mb-0'),
                        Column('expiry_month', css_class='col-md-6 mb-0'),
                    ),
                    css_class="form-group col-md-4"
                ),
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column(
                    FormActions(
                        Submit('submit', 'Submit'),
                        HTML("""
                            <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                            """)
                    ),
                    css_class="form-group col-md-3"
                ),
                Column(
                    HTML("""
                    <table class="table table-sm table-striped">
                        <thead>
                        <tr>
                            <th scope="col" class="text-center">Quantity ({{drug_obj.unit}})</th>
                            <th scope="col" class="text-right">Std Cost ($)</th>
                            <th scope="col" class="text-right">Avg Cost ($)</th>
                            <th scope="col" class="text-right">Final Total ($)</th>
                        </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td id="ds_quantity" class="text-center">&nbsp;</td>
                                <td id="ds_stdcost" class="text-right">&nbsp;</td>
                                <td id="ds_avgcost" class="text-right">&nbsp;</td>
                                <td id="ds_total" class="text-right">&nbsp;</td>
                            </td>
                        </tbody>
                    </table>
                    """),
                    css_class="form-group col-md-9"
                ),
                css_class='form-row',
            ),
        )

    class Meta:
        model = DeliveryItem
        exclude = ['id']

class ItemUpdateModalForm(BSModalForm):

    def __init__(self, *args, **kwargs):
        self.next_url = kwargs.pop('next_url')
        super(ItemUpdateModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-ItemUpdateForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        if self.next_url:
            action_url = "%s?next=%s" % (
                reverse('inventory:ItemUpdateModal', args=(self.instance.pk,)),
                self.next_url
            )
        else:
            action_url = reverse('inventory:ItemUpdateModal', args=(self.instance.pk,))
        self.helper.form_action = action_url
        self.initial['active'] = True
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-8'),
                # Column(UneditableField('cmsid'), css_class='form-group col-md-4'),
                Column('cmsid', css_class='form-group col-md-4'),
                css_class='form-row',
            ),
            Row(
                Column('note', css_class='form-group col-md-8 mb-0'),
                # Column(UneditableField('reg_no'), css_class='form-group col-md-4'),
                Column('reg_no', css_class='form-group col-md-4'),
                css_class='form-row',
            ),
            Row(
                Column('vendor', css_class='form-group col-md-4'),
                Column('category', css_class='form-group col-md-4'),
                Column('item_type', css_class='form-group col-md-4'),
                css_class="form-row",
            ),
            Row(
                Column('is_active'),
                css_class="form-row"
            ),
            Hidden('version', self.instance.version + 1),
            # Hidden('cmsid', self.instance.cmsid),
            # Hidden('reg_no', self.instance.reg_no),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                """),
            ),
        )

    class Meta:
        model = Item
        exclude = ['id', 'date_created', 'last_updated', 'updated_by', ]

class NewItemModalForm(BSModalForm):

    def __init__(self, *args, **kwargs):
        self.drug_obj = kwargs.pop('drug_obj', None)
        self.vendor_obj = kwargs.pop('vendor_obj', None)
        self.next_url = kwargs.pop('next_url')
        super(NewItemModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-NewItemForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        if self.next_url:
            action_url = "%s?next=%s" % (
                reverse('inventory:NewItemModal'),
                self.next_url
            )
        else:
            action_url = reverse('inventory:NewItemModal')
        self.helper.form_action = action_url
        self.initial['active'] = True
        self.initial['item_type'] = ItemType.objects.get(name='Consumable').id
        self.initial['category'] = Category.objects.get(name='Consumable').id
        try:
            self.initial['vendor'] = self.vendor_obj.id
        except:
            pass
        self.helper.layout = Layout(
            Hidden('version', '1'),
            Row(
                Column('name', css_class='form-group col-md-8'),
                Column(UneditableField('cmsid'), css_class='form-group col-md-4'),
                css_class='form-row',
            ),
            Row(
                Column('note', css_class='form-group col-md-8 mb-0'),
                Column(UneditableField('reg_no'), css_class='form-group col-md-4'),
                css_class='form-row',
            ),
            Row(
                Column('vendor', css_class='form-group col-md-4 mb-0'),
                Column('category', css_class='form-group col-md-4 mb-0'),
                Column(UneditableField('item_type'), css_class='form-group col-md-4 mb-0'),
                css_class="form-row",
            ),
            Row(Column('is_active'), css_class='form-row'),
            Hidden('item_type',  ItemType.objects.get(name='Consumable').id),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                """),
            ),
        )

    class Meta:
        model = Item
        exclude = ['id', 'date_created', 'last_updated', 'updated_by', ]

class NewItemForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.drug_obj = kwargs.pop('drug_obj', None)
        self.vendor_obj = kwargs.pop('vendor_obj', None)
        self.next_url = kwargs.pop('next_url')
        super(NewItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-NewItemForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        if self.next_url:
            action_url = "%s?next=%s" % (
                reverse('inventory:NewItem'),
                self.next_url
            )
        else:
            action_url = reverse('inventory:NewItem')
        self.helper.form_action = action_url
        self.initial['active'] = True
        self.initial['item_type'] = ItemType.objects.get(name='Consumable').id
        self.initial['category'] = Category.objects.get(name='Consumable').id
        try:
            self.initial['vendor'] = self.vendor_obj.id
        except:
            pass
        self.helper.layout = Layout(
            Hidden('version', '1'),
            Row(
                Column('name', css_class='form-group col-md-8'),
                Column(UneditableField('cmsid'), css_class='form-group col-md-4'),
                css_class='form-row',
            ),
            Row(
                Column('note', css_class='form-group col-md-8 mb-0'),
                Column(UneditableField('reg_no'), css_class='form-group col-md-4'),
                css_class='form-row',
            ),
            Row(
                Column('vendor', css_class='form-group col-md-4 mb-0'),
                Column('category', css_class='form-group col-md-4 mb-0'),
                Column(UneditableField('item_type'), css_class='form-group col-md-4 mb-0'),
                css_class="form-row",
            ),
            Row(Column('is_active'), css_class='form-row'),
            Hidden('item_type',  ItemType.objects.get(name='Consumable').id),
            FormActions(
                Submit('submit', 'Submit'),
                Button(
                    'back', 'Cancel',
                    css_class='btn-light',
                    onclick="javascript:history.go(-1);"
                ),
            ),
        )

    class Meta:
        model = Item
        exclude = ['id', 'date_created', 'last_updated', 'updated_by', ]

class DeliveryOrderAddDeliveryItemForm(ModelForm):

    expiry_month = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYYMM'})
        )

    def __init__(self, *args, **kwargs):
        self.delivery_obj = kwargs.pop('delivery_obj', None)
        self.cmsitem_obj = kwargs.pop('cmsitem_obj', None)
        self.item_obj = kwargs.pop('item_obj', None)
        self.next_url = kwargs.pop('next_url', None)
        super(DeliveryOrderAddDeliveryItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = True
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-AddDeliveryItemForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        if self.cmsitem_obj:
            self.initial['items_unit'] = self.cmsitem_obj.unit
            url_with_query = "%s?cmsid=%s" % (
                reverse('inventory:DeliveryOrderAddDeliveryItem', args=(self.delivery_obj.id,)),
                self.cmsitem_obj.id 
            )
        else:
            url_with_query = "%s?item=%s" % (
                reverse('inventory:DeliveryOrderAddDeliveryItem', args=(self.delivery_obj.id,)),
                self.item_obj.id 
            )
        if self.next_url:
            url_with_query = url_with_query + "&next=" + self.next_url
        self.helper.form_action = url_with_query
        self.helper.layout = Layout(
            Hidden('version', '1'),
            Hidden('item', self.item_obj.id),
            Hidden('delivery_order', self.delivery_obj.id),
            Row(
                Column(
                    Row(
                        Column('purchase_quantity',css_class='col-md-6 mb-0'),
                        Column('bonus_quantity', css_class='col-md-6 mb-0'),
                    ),
                    css_class="form-group col-md-4",
                ),
                Column(
                    Row(
                        Column('unit_price', css_class='col-md-6 mb-0'),
                        Column('discount', css_class='col-md-6 mb-0'),
                    ),
                    css_class="form-group col-md-4"
                ),
                Column('purchase_unit', css_class="form-group col-md-2"),
                Column('is_sample', css_class="form-group col-md-2"),
                css_class='form-row',
            ),
            Row(
                Column(
                    Row(
                        Column('items_per_purchase', css_class='col-md-6 mb-0'),
                        Column('items_unit', css_class='col-md-6 mb-0'),
                    ),
                    css_class="form-group col-md-4"
                ),
                Column(
                    Row(
                        Column('batch_num', css_class='col-md-6 mb-0'),
                        Column('expiry_month', css_class='col-md-6 mb-0'),
                    ),
                    css_class="form-group col-md-4"
                ),
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column(
                    FormActions(
                        Submit('submit', 'Submit'),
                        Button(
                            'back', 'Cancel',
                            css_class='btn-light',
                            onclick="javascript:history.go(-1);"
                        ),
                    ),
                    css_class="form-group col-md-2"
                ),
                Column(
                    HTML("""
                    <table class="table table-sm table-striped">
                        <thead>
                        <tr>
                            <th scope="col">Quantity ({{cmsitem_obj.unit}})</th>
                            <th scope="col">Std Cost ($)</th>
                            <th scope="col">Avg Cost ($)</th>
                            <th scope="col">Final Total ($)</th>
                        </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td id="ds_quantity">&nbsp;</td>
                                <td id="ds_stdcost">&nbsp;</td>
                                <td id="ds_avgcost">&nbsp;</td>
                                <td id="ds_total">&nbsp;</td>
                            </td>
                        </tbody>
                    </table>
                    """),
                    css_class="form-group col-md-10"
                ),
                css_class='form-row',
            ),
        )
    class Meta:
        model = DeliveryItem
        exclude = ['id', 'version', 'date_created', 'last_updated']