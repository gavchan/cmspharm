from django.urls import path
from . import views

app_name = 'ledger'
urlpatterns = [
    path('expenses/category/<int:pk>/update/', views.ExpenseCategoryUpdate.as_view(), name='ExpenseCategoryUpdate'),
    path('expenses/category/<int:pk>/delete/', views.ExpenseCategoryDelete.as_view(), name='ExpenseCategoryDelete'),
    path('expenses/category/new/', views.NewExpenseCategory.as_view(), name='NewExpenseCategory'),
    path('expenses/category/', views.ExpenseCategoryList.as_view(), name='ExpenseCategoryList'),
    path('expenses/export/csv/', views.ExpenseExportCsv, name='ExpenseExportCsv'),
    path('expenses/<int:pk>/update/', views.ExpenseUpdate.as_view(), name='ExpenseUpdate'),
    path('expenses/<int:pk>/update/modal', views.ExpenseUpdateModal.as_view(), name='ExpenseUpdateModal'),
    path('expenses/<int:pk>/delete/', views.ExpenseDelete.as_view(), name='ExpenseDelete'),
    path('expenses/<int:pk>', views.ExpenseDetail.as_view(), name='ExpenseDetail'),
    # path('expenses/vendor/<int:vendor_id>/new/', views.NewExpenseByVendorModal.as_view(), name='NewExpenseByVendorModal'),
    path('expenses/new/modal', views.NewExpenseModal.as_view(), name='NewExpenseModal'),
    path('expenses/new/', views.NewExpenseSelectVendorView, name='NewExpense'),
    path('expenses/', views.ExpenseList.as_view(), name='ExpenseList'),
    ]
