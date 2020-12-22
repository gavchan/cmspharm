from django.urls import path
from . import views

app_name = 'cmssys'
urlpatterns = [
    path('auditlog/', views.AuditLogList.as_view(), name='AuditLog'),
    ]
