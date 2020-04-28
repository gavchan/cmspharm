from django import forms
from django.forms import ModelForm
from .models import ExpenseCategory, Expense

class NewExpenseCategoryForm(ModelForm):
    class Meta:
        model = ExpenseCategory
        exclude = ['id',]

class ExpenseCategoryUpdateForm(ModelForm):
    class Meta:
        model = ExpenseCategory
        exclude = ['id',]

class NewExpenseForm(ModelForm):

    class Meta:
        model = Expense
        exclude = ['id',]

class ExpenseUpdateForm(ModelForm):

    class Meta:
        model = Expense
        exclude = ['id',] 
