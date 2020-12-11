from django.urls import path
from . import views

app_name = 'drugdb'
urlpatterns = [
    path('', views.RegisteredDrugList.as_view(), name='DrugList'),
    path('drug/<int:pk>', views.RegisteredDrugDetail.as_view(), name='DrugDetail'),

]
