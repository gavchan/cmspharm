from django import forms
from django.forms import ModelForm
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout, Row, Column, Div, HTML, Submit, Button, Hidden,
    Field, Fieldset,
)
from crispy_forms.bootstrap import (
    FormActions,
    FieldWithButtons,
    StrictButton,
    InlineCheckboxes,
    UneditableField,
)
from bootstrap_modal_forms.forms import BSModalForm
from .models import InventoryItem, Supplier


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

class InventoryItemMatchUpdateForm(ModelForm):

    class Meta:
        model = InventoryItem
        exclude = [
            'id', 'version', 'date_created',
            'inventory_item_type',
            'inventory_type',
            'generic_name_chinese',
            'label_name_chinese',
            'location',
            'priority',
            'reorder_status',
            'stock_qty',
            ]
        widgets = {
          'ingredient': forms.Textarea(attrs={'rows':2,}),
        }
        disabled_widget = forms.CheckboxInput(attrs={'disabled': True})

class InventoryItemQuickEditModalForm(BSModalForm):
    def __init__(self, *args, **kwargs):
        self.item_obj = kwargs.pop('item_obj', None)
        self.drug_obj = kwargs.pop('drug_obj', None)
        self.set_match_drug = kwargs.pop('set_match_drug', None)
        super(InventoryItemQuickEditModalForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-InventoryItemQuickEditModalForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'cmsinv:InventoryItemQuickEditModal', args=(self.item_obj.pk, )
            )
        self.initial['version'] = 1
        if self.set_match_drug and self.drug_obj:
            # print(f"{self.item_obj.registration_no} set to {self.drug_obj.reg_no}")
            self.initial['registration_no'] = self.drug_obj.reg_no

        self.helper.layout = Layout(
            Row(
                Column('discontinue', css_class='form-group col-sm-2 mb-0'),
                Column('alias', css_class='form-group col-sm-8 mb-0'),
                Column('registration_no', css_class='form-group col-sm-2 mb-0'),
                css_class='form-row mb-0',
            ),
            Row(
                Column(
                    StrictButton('RegDrug <i class="fad fa-arrow-circle-right"></i>', css_class="btn_update_product btn-sm btn-secondary"), 
                    css_class="form-group col-sm-2 mb-0"
                    ),
                Column('product_name', css_class='form-group col-sm-10 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column(
                    StrictButton('RegDrug <i class="fad fa-arrow-circle-right"></i>', css_class="btn_update_label btn-sm btn-secondary"),
                    css_class="form-group col-sm-2 mb-0"
                ),
                Column('label_name', css_class='form-group col-sm-10 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column(
                    StrictButton('RegDrug <i class="fad fa-arrow-circle-right"></i>', css_class="btn_update_generic btn-sm btn-secondary"),
                    css_class="form-group col-sm-2 mb-0"
                ),
                Column('generic_name', css_class='form-group col-sm-10 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column(
                    StrictButton('RegDrug <i class="fad fa-arrow-circle-right"></i>', css_class="btn_update_ingredient btn-sm btn-secondary"),
                    css_class="form-group col-sm-2 mb-0"
                ),
                Column(
                    Field('ingredient', css_class='form-group col-md-10 mb-0', rows="2"),
                ),
                css_class='form-row'
            ),
            FormActions(
                Submit('submit', 'Submit' ),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                """)
            ),
        )

    class Meta:
        model = InventoryItem
        fields = [
            'discontinue', 'alias', 'registration_no',
            'product_name', 'label_name', 'generic_name', 'ingredient',
        ]

class SupplierQuickEditModalForm(BSModalForm):
    def __init__(self, *args, **kwargs):
        self.supplier_obj = kwargs.pop('supplier_obj', None)
        super(SupplierQuickEditModalForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id_SupplierQuickEditModalForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'cmsinv:SupplierQuickEditModal', args=(self.supplier_obj.pk, )
            )
        self.helper.layout = Layout(
            Row(
                Column('name', css_class="form-group col-sm-4 mb-0"),
                Column(Field('address', rows=3),css_class='form-group col-sm-4 mb-0'),
                Column('supp_type', css_class='form-group col-sm-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('contact_person', css_class="form-group col-sm-4 mb-0"),
                Column('tel_mobile', css_class='form-group col-sm-4 mb-0'),
                Column('tel_home', css_class='form-group col-sm-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('tel_office', css_class="form-group col-sm-4 mb-0"),
                Column('fax', css_class='form-group col-sm-4 mb-0'),
                Column('email', css_class='form-group col-sm-4 mb-0'),
                css_class='form-row',
            ),
            FormActions(
                Submit('submit', 'Submit' ),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                """)
            ),
        )

    class Meta:
        model = Supplier 
        fields = [
            'name', 'address', 'supp_type', 'contact_person', 'tel_mobile',
            'tel_home', 'tel_office', 'tel_office', 'fax', 'email',
        ]