from django.urls import path
from . import views

app_name = 'ledger'
urlpatterns = [
    path('expenses/category/<int:pk>/update/', views.ExpenseCategoryUpdate.as_view(), name='ExpenseCategoryUpdate'),
    path('expenses/category/<int:pk>/delete/', views.ExpenseCategoryDelete.as_view(), name='ExpenseCategoryDelete'),
    path('expenses/category/new/', views.NewExpenseCategory.as_view(), name='NewExpenseCategory'),
    path('expenses/category/', views.ExpenseCategoryList.as_view(), name='ExpenseCategoryList'),
    path('expenses/<int:pk>/update/', views.ExpenseUpdate.as_view(), name='ExpenseUpdate'),
    path('expenses/<int:pk>/update/modal', views.ExpenseUpdatePopup.as_view(), name='ExpenseUpdatePopup'),
    path('expenses/<int:pk>/delete/', views.ExpenseDelete.as_view(), name='ExpenseDelete'),
    path('expenses/<int:pk>', views.ExpenseDetail.as_view(), name='ExpenseDetail'),
    path('expenses/vendor/<int:vendor>/new', views.NewExpense.as_view(), name='NewExpenseFromVendor'),
    path('expenses/new/', views.NewExpense.as_view(), name='NewExpense'),
    path('expenses/', views.ExpenseList.as_view(), name='ExpenseList'),
    ]
