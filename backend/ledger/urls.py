from django.urls import path
from . import views

app_name = 'ledger'
urlpatterns = [
    path('expenses/category/<int:pk>/update/', views.ExpenseCategoryUpdate.as_view(), name='ExpenseCategoryUpdate'),
    path('expenses/category/', views.ExpenseCategoryList.as_view(), name='ExpenseCategoryList'),
    path('expenses/export/csv/', views.ExpenseExportCsv, name='ExpenseExportCsv'),
    path('expenses/<int:pk>/update/', views.ExpenseUpdate.as_view(), name='ExpenseUpdate'),
    path('expenses/<int:pk>/delete/modal', views.ExpenseDeleteModal.as_view(), name='ExpenseDeleteModal'),
    # path('expenses/vendor/<int:vendor_id>/new/', views.NewExpenseByVendorModal.as_view(), name='NewExpenseByVendorModal'),
    path('expenses/new/modal', views.NewExpenseModal.as_view(), name='NewExpenseModal'),
    path('expenses/new/selectvendor', views.NewExpenseSelectVendorView, name='NewExpenseSelectVendor'),
    path('expenses/new', views.NewExpense.as_view(), name='NewExpense'),
    path('expenses/', views.ExpenseList.as_view(), name='ExpenseList'),
    ]