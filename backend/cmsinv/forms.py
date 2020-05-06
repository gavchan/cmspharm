from django import forms
from django.forms import ModelForm
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Fieldset, Submit, Button
from crispy_forms.bootstrap import FormActions
from bootstrap_modal_forms.forms import BSModalForm
from .models import InventoryItem


class InventoryItemUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(InventoryItemUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False 
        self.helper.form_id = 'id-InventoryItemForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('cmsinv:InventoryItemUpdate', args=(self.instance.pk,))
        self.helper.layout = Layout(
            Row(
                Column('registration_no', css_class='form-group col-md-4 mb-0'),
                Column('clinic_drug_no', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('product_name', css_class='form-group col-md-4 mb-0'),
                Column('product_name_chinese', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('label_name', css_class='form-group col-md-4 mb-0'),
                Column('label_name_chinese', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('generic_name', css_class='form-group col-md-4 mb-0'),
                Column('generic_name_chinese', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('alias', css_class='form-group col-md-4 mb-0'),
                Column('certificate_holder', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('standard_cost', css_class='form-group col-md-4 mb-0'),
                Column('avg_cost', css_class='form-group, col-md-4 mb-0'),
                Column('unit_price', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('stock_qty', css_class='form-group col-md-4 mb-0'),
                Column('expected_qty', css_class='form-group col-md-4 mb-0'),
                Column('reorder_level', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                css_class='form-row',
            ),
            Row(
                Column('location', css_class='form-group col-md-4 mb-0'),
                Column('priority', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('is_master_drug_list', css_class='form-group col-md-4 mb-0'),
                Column('discontinue', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('is_clinic_drug_list', css_class='form-group col-md-4 mb-0'),
                Column('dangerous_sign', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column(Field('ingredient', css_class='form-group col-md-12 mb-0', rows="1")),
                css_class='form-row',
            ),
            Row(
                Column(Field('remarks', css_class='form-group col-md-12 mb-0', rows="1")),
                css_class='form-row',
            ),
            Row(
                Column('dosage', css_class='form-group col-md-4 mb-0'),
                Column('mini_dosage_unit', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('frequency', css_class='form-group col-md-4 mb-0'),
                Column('duration', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('unit', css_class='form-group col-md-4 mb-0'),
                Column('mini_dispensary_unit', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('instruction', css_class='form-group col-md-12 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('advisory', css_class='form-group col-md-12 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('version', css_class='form-group col-md-12 mb-0'), 
                Column('inventory_item_type', css_class='form-group col-md-12 mb-0'),
                css_class='form-row',
            ),
            FormActions(
                Submit('submit', 'Submit'),
                Button('cancel', 'Cancel'),
            ),
        )

    class Meta:
        model = InventoryItem
        exclude = ['id',]

