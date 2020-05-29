from datetime import date
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
)
from bootstrap_datepicker_plus import DatePickerInput
from bootstrap_modal_forms.forms import BSModalForm
from .models import ExpenseCategory, Expense, PaymentMethod


class NewExpenseCategoryForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(NewExpenseCategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-ExpenseCategoryForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'ledger:NewExpenseCategory')
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('description', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('label', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('active', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <a class="btn btn-light" href="{% url 'ledger:ExpenseCategoryList' %}">Cancel</a>
                """),
            ),
        )

    class Meta:
        model = ExpenseCategory
        exclude = ['id', ]


class ExpenseCategoryUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExpenseCategoryUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-ExpenseCategoryForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'ledger:ExpenseCategoryUpdate', args=(self.instance.pk,))
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('description', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('label', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('active', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <a class="btn btn-light" href="{% url 'ledger:ExpenseCategoryList' %}">Cancel</a>
                """),
            ),
        )

    class Meta:
        model = ExpenseCategory
        exclude = ['id', ]


class NewExpenseForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.vendor_obj= kwargs.pop('vendor_obj', None)
        if self.vendor_obj:
            self.initial['vendor'] = self.vendor_obj.pk
        super(NewExpenseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-ExpenseForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'ledger:NewExpense')
        #self.initial['entry_date'] = date.today().strftime('%Y-%m-%d')
        today_date = date.today().strftime('%Y-%m-%d')
        self.initial['payment_method'] = PaymentMethod.objects.get(name='Cheque').pk 
        self.initial['version'] = 1

        self.helper.layout = Layout(
            Hidden('entry_date', today_date),
            Hidden('version', '1'),
            Row(
                Column(
                    FieldWithButtons('vendor', StrictButton('<i class="far fa-user-plus"></i>', id='add_vendor_button', css_class='btn-secondary')),
                    css_class='form-group col-md-8 mb-0'
                    ),
                Column('category', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('expected_date', css_class='form-group col-md-4 mb-0'),
                Column('amount', css_class='form-group col-md-4 mb-0'),
                Column('description', css_class="form-group col-md-4 mb-0"),
                css_class='form-row',
            ),
            Row(
                Column('payment_ref', css_class='form-group col-md-4 mb-0'),
                Column('payment_method', css_class='form-group col-md-4 mb-0'),
                Column('payee', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('invoice_no', css_class='form-group col-md-4 mb-0'),
                Column('invoice_date', css_class='form-group col-md-4 mb-0'),
                Column('settled_date', css_class='form-group col-md-4 mb-0'),
                css_class="form-row",
            ),
            Row(
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                Column(Field('remarks', css_class='form-group col-md-8 mb-0', rows="1")),
                css_class="form-row",            
            ),
            FormActions(
                Submit('submit', 'Submit'),
                Button('cancel', 'Cancel', onclick="window.location.href = '{}';".format(reverse('ledger:ExpenseList')))
            ),
        )

    class Meta:
        model = Expense
        exclude = ['id', ]
        widgets = {
                    'expected_date': DatePickerInput(
                        options={
                            "format": "YYYY-MM-DD",
                            "showClose": True,
                            "showClear": True,
                            "showTodayButton": True,
                        }
                    ),
                    'settled_date': DatePickerInput(
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

class ExpenseUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExpenseUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-ExpenseForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'ledger:ExpenseUpdate', args=(self.instance.pk,))

        self.helper.layout = Layout(
            Row(
                Column('entry_date', css_class='form-group col-md-4 mb-0'),
                Column('version', css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column('vendor', css_class='form-group col-md-8 mb-0'),
                Column('category', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('expected_date', css_class='form-group col-md-4 mb-0'),
                Column('amount', css_class='form-group col-md-4 mb-0'),
                Column('description', css_class="form-group col-md-4 mb-0"),
                css_class='form-row',
            ),
            Row(
                Column('payee', css_class='form-group col-md-4 mb-0'),
                Column('payment_ref', css_class='form-group col-md-4 mb-0'),
                Column('payment_method', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('invoice_no', css_class='form-group col-md-4 mb-0'),
                Column('invoice_date', css_class='form-group col-md-4 mb-0'),
                Column('settled_date', css_class='form-group col-md-4 mb-0'),
                css_class="form-row",
            ),
            Row(
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                Column(Field('remarks', css_class='form-group col-md-8 mb-0', rows="1")),
                css_class="form-row",            
            ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <a class="btn btn-light" href="{% url 'ledger:ExpenseList' %}">Cancel</a>
                """)
            ),
        )

    class Meta:
        model = Expense
        exclude = ['id', ]
        widgets = {
                    'entry_date': DatePickerInput(
                        options={
                            "format": "YYYY-MM-DD",
                            "showClose": True,
                            "showClear": True,
                            "showTodayButton": True,
                        }
                    ),
                    'expected_date': DatePickerInput(
                        options={
                            "format": "YYYY-MM-DD",
                            "showClose": True,
                            "showClear": True,
                            "showTodayButton": True,
                        }
                    ),
                    'settled_date': DatePickerInput(
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

class ExpenseUpdateModalForm(BSModalForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ExpenseUpdateModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-ExpenseForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'ledger:ExpenseUpdatePopup', args=(self.instance.pk,))

        self.helper.layout = Layout(
            Row(
                Column('entry_date', css_class='form-group col-md-4 mb-0'),
                Column('version', css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column('vendor', css_class='form-group col-md-8 mb-0'),
                Column('category', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('expected_date', css_class='form-group col-md-4 mb-0'),
                Column('amount', css_class='form-group col-md-4 mb-0'),
                Column('description', css_class="form-group col-md-4 mb-0"),
                css_class='form-row',
            ),
            Row(
                Column('payee', css_class='form-group col-md-4 mb-0'),
                Column('payment_ref', css_class='form-group col-md-4 mb-0'),
                Column('payment_method', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('invoice_no', css_class='form-group col-md-4 mb-0'),
                Column('invoice_date', css_class='form-group col-md-4 mb-0'),
                Column('settled_date', css_class='form-group col-md-4 mb-0'),
                css_class="form-row",
            ),
            Row(
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                Column(Field('remarks', css_class='form-group col-md-8 mb-0', rows="1")),
                css_class="form-row",            
            ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                """)
            ),
        )

    class Meta:
        model = Expense
        exclude = ['id', ]
        widgets = {
                    'entry_date': DatePickerInput(
                        options={
                            "format": "YYYY-MM-DD",
                            "showClose": True,
                            "showClear": True,
                            "showTodayButton": True,
                        }
                    ),
                    'expected_date': DatePickerInput(
                        options={
                            "format": "YYYY-MM-DD",
                            "showClose": True,
                            "showClear": True,
                            "showTodayButton": True,
                        }
                    ),
                    'settled_date': DatePickerInput(
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
