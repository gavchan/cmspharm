from django import forms
from django.forms import ModelForm
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Vendor, Item, DeliveryOrder, DeliveryItem
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
from datetime import date

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

class NewDeliveryOrderModalForm(BSModalForm):
    
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
            Hidden('is_paid', False),
            Row(
                Column(
                    FieldWithButtons('vendor', StrictButton('<i class="far fa-user-plus"></i>', id='add_vendor_button', css_class='btn-secondary')),
                    css_class='form-group col-md-8 mb-0'
                    ),
                Column('received_date', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('invoice_no', css_class='form-group col-md-8 mb-0'),
                Column('invoice_date', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                Column('amount', css_class='form-group col-md-4 mb-0'),
                Column('due_date', css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column(Field('remarks', css_class='form-group col-md-12 mb-0', rows="2")),
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
                    'received_date': DatePickerInput(
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
                    'due_date': DatePickerInput(
                        options={
                            "format": "YYYY-MM-DD",
                            "showClose": True,
                            "showClear": True,
                            "showTodayButton": True,
                        }
                    ),
                }

class DeliveryOrderUpdateModalForm(BSModalForm):
    
    def __init__(self, *args, **kwargs):
        super(DeliveryOrderUpdateModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-DeliveryOrderUpdateForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'inventory:DeliveryOrderUpdateModal', args=(self.instance.pk,))
        #self.initial['entry_date'] = date.today().strftime('%Y-%m-%d')
        today_date = date.today().strftime('%Y-%m-%d')
        self.helper.layout = Layout(
            Row(
                Column(
                    UneditableField('vendor'),
                    css_class='form-group col-md-8 mb-0'
                    ),
                Column('received_date', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('invoice_no', css_class='form-group col-md-8 mb-0'),
                Column('invoice_date', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                Column('amount', css_class='form-group col-md-4 mb-0'),
                Column('due_date', css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column(Field('remarks', css_class='form-group col-md-12 mb-0', rows="2")),
                css_class="form-row",            
            ),
            Hidden('vendor', self.instance.vendor.pk),
            Hidden('version', self.instance.version + 1),
            FormActions(
                Submit('submit', 'Submit'),
            ),
        )

    class Meta:
        model = DeliveryOrder
        exclude = ['id', 'items', 'is_paid', 'bill, ''date_created', 'last_updated',]
        widgets = {
                    'received_date': DatePickerInput(
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
                    'due_date': DatePickerInput(
                        options={
                            "format": "YYYY-MM-DD",
                            "showClose": True,
                            "showClear": True,
                            "showTodayButton": True,
                        }
                    )
                }
class DeliveryItemUpdateModalForm(BSModalForm):

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
                                <td id="ds_quantity" class="text-monospace text-center">&nbsp;</td>
                                <td id="ds_stdcost" class="text-monospace text-right">&nbsp;</td>
                                <td id="ds_avgcost" class="text-monospace text-right">&nbsp;</td>
                                <td id="ds_total" class="text-monospace text-right">&nbsp;</td>
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

class NewItemFromVendorForm(ModelForm):
    class Meta:
        model = InventoryItem
        exclude = ['id', 'version', 'date_created',]

class NewItemModalForm(BSModalForm):

    def __init__(self, *args, **kwargs):
        self.drug_obj = kwargs.pop('drug_obj', None)
        print(f"args={args}; kwargs={kwargs}")
        super(NewItemModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.render_unmentioned_fields = True 
        self.helper.form_id = 'id-NewItemForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'inventory:NewItemModal', kwargs={'drug_id': self.drug_obj.id,}
            )
        if self.drug_obj:
            self.initial['name'] = self.drug_obj.name
            self.initial['label'] = self.drug_obj.name
            self.initial['item_type'] = 'DRUG'
        self.initial['active'] = True
        self.helper.layout = Layout(
            Hidden('version', '1'),
            Hidden('item_type', 'DRUG'),
            Hidden('reg_no', self.drug_obj.reg_no),
            Row(
                Column('name', css_class='form-group col-md-5 mb-0'),
                Column('alias', css_class='form-group col-md-5 mb-0'),
                Column('item_unit', css_class='form-group col-md-2 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('label', css_class='form-group col-md-5 mb-0'),
                Column('generic_name', css_class='form-group col-md-5 mb-0'),
                Column(UneditableField('clinic_no'), css_class='form-group col-md-2 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('description', css_class='form-group col-md-5 mb-0'),
                Column(Field('remarks', css_class='form-control col-md-5 mb-0', rows="1")),
                Column(
                        Row('active'),
                        Row('dangerous_drug'),
                        css_class='form-group col-md-2 mb-0'),
                css_class="form-row",
            ),
            FormActions(
                Submit('submit', 'Submit'),
            ),
        )

    class Meta:
        model = Item
        exclude = ['id', 'date_created', 'last_updated', 'updated_by', ]

class ItemUpdateForm(ModelForm):
    class Meta:
        model = Item
        exclude = ['id', 'version', 'date_created',]

class DeliveryOrderAddDeliveryItemForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.delivery_obj = kwargs.pop('delivery_obj', None)
        self.drug_obj = kwargs.pop('drug_obj', None)
        self.item_obj = kwargs.pop('item_obj', None)
        
        super(DeliveryOrderAddDeliveryItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = True
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-AddDeliveryItemForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'inventory:DeliveryOrderAddDeliveryItem', args=(self.delivery_obj.id, self.drug_obj.id,)
            )
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
                        HTML("""
                            <button id="btn_cancel" class="btn btn-outline"
                            >Cancel</button>
                            """)
                    ),
                    css_class="form-group col-md-2"
                ),
                Column(
                    HTML("""
                    <table class="table table-sm table-striped">
                        <thead>
                        <tr>
                            <th scope="col">Quantity ({{drug_obj.unit}})</th>
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