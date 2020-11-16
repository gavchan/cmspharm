from django import forms
from django.urls import reverse
from django.forms import ModelForm
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


class BillDrugDeliveryAddDrugModalForm(BSModalForm):

    def __init__(self, *args, **kwargs):
        # self.request = kwargs.pop('request', None)
        self.bill_obj = kwargs.pop('bill_obj', None)
        self.drug_obj = kwargs.pop('drug_obj', None)
        self.action = kwargs.pop('action', None)
        super(BillDrugDeliveryAddDrugModalForm, self).__init__(*args, **kwargs)
        self.bill_id = self.bill_obj.id
        print(self.bill_obj.id, self.drug_obj.reg_no)
        
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-DrugDeliveryBillAddForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'drugdb:BillDrugDeliveryAddDrugModal', args=(self.bill_obj.id, self.drug_obj.reg_no,)
            )
        self.initial['product_name'] = self.drug_obj.name
        self.initial['reg_no'] = self.drug_obj.reg_no
        self.initial['version'] = 1
        self.initial['received_date'] = self.bill_obj.invoice_date
        self.initial['delivery_note_no'] = self.bill_obj.invoice_no
        self.ingredient_str = f"<p><em>Ingredients:</em> {self.drug_obj.ingredients}</p>"
        self.helper.layout = Layout(
            Row(
                Hidden('version', '1'),
                Hidden('bill', self.bill_obj.id),
                Hidden('product_name', self.drug_obj.name),
                Hidden('reg_no', self.drug_obj.reg_no),
                Column(UneditableField('product_name', css_class='form-control'), css_class='col-md-4 mb-0'),
                Column(UneditableField('reg_no', css_class='form-control'), css_class='col-md-4 mb-0'),
            ),
            Row(
                Column(HTML(self.ingredient_str)),
                css_class='form-row border-bottom',
            ),
            Row(
                Column('received_date', css_class='form-group col-md-8 mb-0'),
                Column('delivery_note_no', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('purchase_quantity', css_class='form-group col-md-4 mb-0'),
                Column('bonus_quantity', css_class='form-group col-md-4 mb-0'),
                Column('purchase_unit', css_class="form-group col-md-4 mb-0"),
                css_class='form-row',
            ),
            Row(
                Column('unit_price', css_class='form-group col-md-4 mb-0'),
                Column('discount', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('items_per_purchase', css_class='form-group col-md-4 mb-0'),
                Column('items_unit', css_class='form-group col-md-4 mb-0'),
                css_class="form-row",
            ),
            Row(
                Column('batch_num', css_class='form-group col-md-4 mb-0'),
                Column('expiry_month', css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column('remark', css_class='form-group col-md-4 mb-0'),
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                css_class="form-row",            
            ),
            
            FormActions(
                Submit('submit', self.action),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                """)
            ),
        )

    class Meta:
        model = DrugDelivery
        exclude = ['id']
        widgets = {
                    'received_date': DatePickerInput(
                        options={
                            "format": "YYYY-MM-DD",
                            "showClose": True,
                            "showClear": True,
                            "showTodayButton": True,
                        }
                    ),
                    'expiry_month': DatePickerInput(
                        options={
                            "format": "YYYYMMDD",
                            "showClose": True,
                            "showClear": True,
                            "showTodayButton": True,
                        }
                    ),
                }

