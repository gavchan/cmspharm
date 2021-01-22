from datetime import date
from django import forms
from django.forms import ModelForm
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout, Row, Column, Div, HTML, Submit, Button, Hidden,
    Field, Fieldset, 
)
from crispy_forms.bootstrap import (
    FormActions,
    FieldWithButtons,
    PrependedText,
    StrictButton,
    UneditableField,
)
from bootstrap_datepicker_plus import DatePickerInput
from bootstrap_modal_forms.forms import BSModalForm
from .models import ExpenseCategory, Expense, PaymentMethod, Vendor, Income


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

class ExpenseUpdateForm(ModelForm):

    entry_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    invoice_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    expected_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'})
        )
    
    def __init__(self, *args, **kwargs):
        # self.request = kwargs.pop('request', None)
        super(ExpenseUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.render_required_files = True
        self.helper.form_id = 'id-ExpenseForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'ledger:ExpenseUpdate', args=(self.instance.pk,))
        print(self.instance)
        self.helper.layout = Layout(
            Row(
                Div(HTML("""
                    <label for="entry_date">Entry date</label>*
                    <div class="input-group date" id="datepicker_entry_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_entry_date"
                            placeholder="YYYY-MM-DD"
                            name="entry_date"
                            value="{{ expense_obj.entry_date|date:'Y-m-d' }}"
                        >
                        <div class="input-group-append" data-target="#datepicker_entry_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                Column(Field('version', disabled=True),
                    css_class='form-group col-md-4 mb-0'),
                Column('permanent', css_class='form-group col-md-4'),
            ),
            Row(
                Column(UneditableField('vendor'), css_class='form-group col-md-8 mb-0'),
                Column('payee', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('category', css_class='form-group col-md-4 mb-0'),
                Column('invoice_no', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="invoice_date">Invoice date</label>
                    <div class="input-group date" id="datepicker_invoice_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_invoice_date"
                            placeholder="YYYY-MM-DD"
                            name="invoice_date"
                            value="{{ expense_obj.invoice_date|date:'Y-m-d' }}"
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
                Column('payment_method', css_class='form-group col-md-4 mb-0'),
                Column(PrependedText('amount', '$'), css_class='form-group col-md-4 mb-0'),
                Column('description', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('payment_ref', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="expected_date">Payment date</label>*
                    <div class="input-group date" id="datepicker_expected_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_expected_date"
                            placeholder="YYYY-MM-DD"
                            name="expected_date"
                            value="{{ expense_obj.expected_date|date:'Y-m-d' }}"
                        >
                        <div class="input-group-append" data-target="#datepicker_expected_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                css_class="form-row",),
            Row(
                Column(
                    Field('remarks', css_class='form-group col-md-8 mb-0', rows="1")),
                css_class="form-row",
            ),
            Hidden('vendor', self.instance.vendor.pk),
            Hidden('version', self.instance.version +1),
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
        model = Expense
        exclude = ['id', ]
        

class NewExpenseForm(ModelForm):

    invoice_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    expected_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'})
        )

    def __init__(self, *args, **kwargs):
        self.vendor_obj = kwargs.pop('vendor_obj', None)

        super(NewExpenseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-ExpenseForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'ledger:NewExpense')
        #self.initial['entry_date'] = timezone.now().strftime('%Y-%m-%d')
        today_date = timezone.now().strftime('%Y-%m-%d')
        self.initial['payment_method'] = PaymentMethod.objects.get(
            name='Cheque').pk
        self.initial['version'] = 1
        if self.vendor_obj:
            self.initial['vendor'] = self.vendor_obj.id
            self.initial['payee'] = self.vendor_obj.name
            self.initial['category'] = self.vendor_obj.default_exp_category if not None else ''
            self.initial['description'] = self.vendor_obj.default_description if not None else ''
        self.helper.layout = Layout(
            Hidden('next', self.helper.form_action),
            Hidden('entry_date', today_date),
            Hidden('version', '1'),
            Row(
                Column(
                    'vendor',
                    # FieldWithButtons('vendor', StrictButton(
                    #     '<i class="far fa-user-plus"></i>', id='add_vendor_button', css_class='btn-secondary')),
                    css_class='form-group col-md-8 mb-0'
                ),
                Column('payee', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('category', css_class='form-group col-md-4 mb-0'),
                Column('invoice_no', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="invoice_date">Invoice date</label>
                    <div class="input-group date" id="datepicker_invoice_date" data-target-input="nearest">
                        <input type="text" 
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
                Column('payment_method', css_class='form-group col-md-4 mb-0'),
                Column('amount', css_class='form-group col-md-4 mb-0'),
                Column('description', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('payment_ref', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="expected_date">Payment date</label>*
                    <div class="input-group date" id="datepicker_expected_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_expected_date"
                            placeholder="YYYY-MM-DD"
                            name="expected_date"
                        >
                        <div class="input-group-append" data-target="#datepicker_expected_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                css_class="form-row",),
            Row(
                Column(
                    Field('remarks', css_class='form-group col-md-8 mb-0', rows="1")),
                css_class="form-row",
            ),
            FormActions(
                Submit('submit', 'Submit'),
                Button(
                    'back', 'Cancel',
                    css_class='btn-light',
                    onclick="javascript:history.go(-1);"
                )
            ),
        )

    class Meta:
        model = Expense
        exclude = ['id', ]

class NewExpenseModalForm(BSModalForm):

    entry_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    invoice_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    expected_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'})
        )

    def __init__(self, *args, **kwargs):
        self.vendor_obj = kwargs.pop('vendor_obj', None)

        super(NewExpenseModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-ExpenseForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'ledger:NewExpenseModal')
        #self.initial['entry_date'] = timezone.now().strftime('%Y-%m-%d')
        today_date = timezone.now().strftime('%Y-%m-%d')
        self.initial['payment_method'] = PaymentMethod.objects.get(
            name='Cheque').pk
        self.initial['version'] = 1
        if self.vendor_obj:
            self.initial['vendor'] = self.vendor_obj.id
            self.initial['payee'] = self.vendor_obj.name
            self.initial['category'] = self.vendor_obj.default_exp_category if not None else ''
            self.initial['description'] = self.vendor_obj.default_description if not None else ''
        self.helper.layout = Layout(
            Hidden('entry_date', today_date),
            Hidden('version', '1'),
            Row(
                Column(
                    'vendor',
                    # FieldWithButtons('vendor', StrictButton(
                    #     '<i class="far fa-user-plus"></i>', id='add_vendor_button', css_class='btn-secondary')),
                    css_class='form-group col-md-8 mb-0'
                ),
                Column('payee', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('category', css_class='form-group col-md-4 mb-0'),
                Column('invoice_no', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="invoice_date">Invoice date</label>
                    <div class="input-group date" id="datepicker_invoice_date" data-target-input="nearest">
                        <input type="text" 
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
                Column('payment_method', css_class='form-group col-md-4 mb-0'),
                Column('amount', css_class='form-group col-md-4 mb-0'),
                Column('description', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('payment_ref', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="expected_date">Payment date</label>*
                    <div class="input-group date" id="datepicker_expected_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_expected_date"
                            placeholder="YYYY-MM-DD"
                            name="expected_date"
                        >
                        <div class="input-group-append" data-target="#datepicker_expected_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                css_class="form-row",),
            Row(
                Column(
                    Field('remarks', css_class='form-group col-md-8 mb-0', rows="1")),
                css_class="form-row",
            ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                """),
            ),
        )

    class Meta:
        model = Expense
        exclude = ['id', ]

class ExpenseUpdateModalForm(BSModalForm):

    entry_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    invoice_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    expected_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'})
        )

    def __init__(self, *args, **kwargs):
        # self.request = kwargs.pop('request', None)
        super(ExpenseUpdateModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-ExpenseForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'ledger:ExpenseUpdateModal', args=(self.instance.pk,))

        self.helper.layout = Layout(
            Row(
                Div(HTML("""
                    <label for="entry_date">Entry date</label>
                    <div class="input-group date" id="datepicker_entry_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_entry_date"
                            placeholder="YYYY-MM-DD"
                            name="entry_date"
                            value="{{ expense_obj.entry_date|date:'Y-m-d' }}"
                        >
                        <div class="input-group-append" data-target="#datepicker_entry_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                Column(Field('version', disabled=True),
                    css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column(UneditableField('vendor'), css_class='form-group col-md-8 mb-0'),
                Column('payee', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('category', css_class='form-group col-md-4 mb-0'),
                Column('invoice_no', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="invoice_date">Invoice date</label>
                    <div class="input-group date" id="datepicker_invoice_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_invoice_date"
                            placeholder="YYYY-MM-DD"
                            name="invoice_date"
                            value="{{ expense_obj.invoice_date|date:'Y-m-d' }}"
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
                Column('payment_method', css_class='form-group col-md-4 mb-0'),
                Column(PrependedText('amount', '$'), css_class='form-group col-md-4 mb-0'),
                Column('description', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('payment_ref', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="expected_date">Payment date</label>
                    <div class="input-group date" id="datepicker_expected_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_expected_date"
                            placeholder="YYYY-MM-DD"
                            name="expected_date"
                            value="{{ expense_obj.expected_date|date:'Y-m-d' }}"
                        >
                        <div class="input-group-append" data-target="#datepicker_expected_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                css_class="form-row",),
            Row(
                Column(
                    Field('remarks', css_class='form-group col-md-8 mb-0', rows="1")),
                css_class="form-row",
            ),
            Hidden('vendor', self.instance.vendor.pk),
            Hidden('version', self.instance.version +1),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                """),
            ),
        )

    class Meta:
        model = Expense
        exclude = ['id', ]

class DeliveryPaymentModalForm(BSModalForm):
    
    expected_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'})
        )
    def __init__(self, *args, **kwargs):
        self.delivery_obj = kwargs.pop('delivery_obj', None)
        super(DeliveryPaymentModalForm, self).__init__(*args, **kwargs)
        if self.delivery_obj:
            print(f"Payment for delivery # {self.delivery_obj.id}")
        else:
            print(f"Error: no delivery_obj")
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-DeliveryPaymentForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'ledger:DeliveryPaymentModal', args=(self.delivery_obj.id,))
        #self.initial['entry_date'] = timezone.now().strftime('%Y-%m-%d')
        today_date = timezone.now().strftime('%Y-%m-%d')
        self.exp_category_drug = ExpenseCategory.objects.get(code='1').id
        self.initial['entry_date'] = today_date
        self.initial['payment_method'] = PaymentMethod.objects.get(
            name='Cheque').pk
        self.initial['vendor'] = self.delivery_obj.vendor.id
        self.initial['payee'] = self.delivery_obj.vendor.name
        self.initial['invoice_no'] = self.delivery_obj.invoice_no
        self.initial['invoice_date'] = self.delivery_obj.invoice_date
        self.initial['other_ref'] = self.delivery_obj.other_ref
        self.initial['amount'] = self.delivery_obj.amount
        self.initial['category'] = self.exp_category_drug
        self.initial['description'] = 'Drug/Supplement'
            
        self.helper.layout = Layout(
            
            Row(
                Column(
                    UneditableField('vendor'),
                    css_class='form-group col-md-8 mb-0'
                ),
                Column('payee', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column(UneditableField('category'), css_class='form-group col-md-4 mb-0'),
                Column(UneditableField('invoice_no'), css_class='form-group col-md-4 mb-0'),
                Column(UneditableField('invoice_date'), css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('payment_method', css_class='form-group col-md-4 mb-0'),
                Column('amount', css_class='form-group col-md-4 mb-0'),
                Column('description', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('payment_ref', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="expected_date">Payment date</label>*
                    <div class="input-group date" id="datepicker_expected_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_expected_date"
                            placeholder="YYYY-MM-DD"
                            name="expected_date"
                        >
                        <div class="input-group-append" data-target="#datepicker_expected_date" data-toggle="datetimepicker">
                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                        </div>
                    </div>
                    """),
                    css_class='form-group col-md-4'
                ),
                Column('other_ref', css_class='form-group col-md-4 mb-0'),
                css_class="form-row",),
            Row(
                Column(
                    Field('remarks', css_class='form-group col-md-8 mb-0', rows="1")),
                css_class="form-row",
            ),
            Hidden('entry_date', today_date),
            Hidden('version', '1'),
            Hidden('vendor', self.delivery_obj.vendor.id),
            Hidden('invoice_no', self.delivery_obj.invoice_no),
            Hidden('invoice_date', self.delivery_obj.invoice_date),
            Hidden('category', self.exp_category_drug),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                """),
            ),
        )

    class Meta:
        model = Expense
        exclude = ['id', 'date_created', 'last_updated']


class NewIncomeModalForm(BSModalForm):

    invoice_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    expected_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'})
        )
    def __init__(self, *args, **kwargs):

        super(NewIncomeModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-IncomeForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'ledger:NewIncomeModal')
        today_date = timezone.now().strftime('%Y-%m-%d')
        print(today_date)
        self.initial['payment_method'] = PaymentMethod.objects.get(
            name='Bank Tx').pk
        self.helper.layout = Layout(
            Hidden('version', 1),
            Hidden('entry_date', today_date),
            Row(
                Column(
                    'payer',
                    # FieldWithButtons('vendor', StrictButton(
                    #     '<i class="far fa-user-plus"></i>', id='add_vendor_button', css_class='btn-secondary')),
                    css_class='form-group col-md-8 mb-0'
                ),
                Column('payment_method', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('amount', css_class='form-group col-md-4 mb-0'),
                Column('payment_ref', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="expected_date">Payment date</label>*
                    <div class="input-group date" id="datepicker_expected_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_expected_date"
                            placeholder="YYYY-MM-DD"
                            name="expected_date"
                        >
                        <div class="input-group-append" data-target="#datepicker_expected_date" data-toggle="datetimepicker">
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
                Column('invoice_no', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="invoice_date">Invoice date</label>
                    <div class="input-group date" id="datepicker_invoice_date" data-target-input="nearest">
                        <input type="text" 
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
                Column('description', css_class='form-group col-md-4 mb-0'),
                Field('remarks', css_class='form-group col-md-8 mb-0', rows="1"),
                css_class="form-row",
            ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                """),
            ),
        )

    class Meta:
        model = Income
        exclude = ['id', ]


class IncomeUpdateModalForm(BSModalForm):

    invoice_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    expected_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'})
        )
    def __init__(self, *args, **kwargs):

        super(IncomeUpdateModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = False
        self.helper.form_id = 'id-IncomeForm'
        self.helper.form_class = 'cmmForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse(
            'ledger:IncomeUpdateModal', args=(self.instance.pk,))
        self.helper.layout = Layout(
            Row(
                Column(
                    'payer',
                    # FieldWithButtons('vendor', StrictButton(
                    #     '<i class="far fa-user-plus"></i>', id='add_vendor_button', css_class='btn-secondary')),
                    css_class='form-group col-md-8 mb-0'
                ),
                Column('payment_method', css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('amount', css_class='form-group col-md-4 mb-0'),
                Column('payment_ref', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="expected_date">Payment date</label>*
                    <div class="input-group date" id="datepicker_expected_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_expected_date"
                            placeholder="YYYY-MM-DD"
                            name="expected_date"
                            value="{{ income_obj.expected_date|date:'Y-m-d' }}"
                        >
                        <div class="input-group-append" data-target="#datepicker_expected_date" data-toggle="datetimepicker">
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
                Column('invoice_no', css_class='form-group col-md-4 mb-0'),
                Div(HTML("""
                    <label for="invoice_date">Invoice date</label>
                    <div class="input-group date" id="datepicker_invoice_date" data-target-input="nearest">
                        <input type="text" 
                            class="form-control datetimepicker-input"
                            data-target="#datepicker_invoice_date"
                            placeholder="YYYY-MM-DD"
                            name="invoice_date"
                            value="{{ income_obj.invoice_date|date:'Y-m-d' }}"
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
                Column('description', css_class='form-group col-md-4 mb-0'),
                Field('remarks', css_class='form-group col-md-8 mb-0', rows="1"),
                css_class="form-row",
            ),
            FormActions(
                Submit('submit', 'Submit'),
                HTML("""
                <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                """),
            ),
        )

    class Meta:
        model = Income
        exclude = ['id', 'version', 'entry_date']
