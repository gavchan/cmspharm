from django import forms
from django.forms import ModelForm
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Fieldset, Submit, Button
from crispy_forms.bootstrap import FormActions

from .models import ExpenseCategory, Expense


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
                Button('cancel', 'Cancel'),
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
                Button('cancel', 'Cancel'),
            ),
        )

    class Meta:
        model = ExpenseCategory
        exclude = ['id', ]


class NewExpenseForm(ModelForm):

    class Meta:
        model = Expense
        exclude = ['id', ]


class ExpenseUpdateForm(ModelForm):

    class Meta:
        model = Expense
        exclude = ['id', ]
