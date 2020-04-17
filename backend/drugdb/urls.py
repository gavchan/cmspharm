from django.urls import path
from . import views

app_name = 'drugdb'
urlpatterns = [
    path('drugs/', views.RegisteredDrugList.as_view(), name='DrugList'),
]