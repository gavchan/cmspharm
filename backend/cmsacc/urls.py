from django.urls import path
from . import views

app_name = 'cmsacc'
urlpatterns = [
    path('payments/today', views.PaymentsToday.as_view(), name='PaymentToday'),
    ]
