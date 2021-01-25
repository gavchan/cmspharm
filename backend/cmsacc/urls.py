from django.urls import path
from . import views

app_name = 'cmsacc'
urlpatterns = [
    path('cashbook/', views.CashbookToday.as_view(), name='CashbookToday'),
    ]
