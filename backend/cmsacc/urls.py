from django.urls import path
from . import views

app_name = 'cmsacc'
urlpatterns = [
    path('bills/today/', views.BillToday.as_view(), name='BillToday'),
    ]
