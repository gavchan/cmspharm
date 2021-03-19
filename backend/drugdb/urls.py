from django.urls import path
from . import views

app_name = 'drugdb'
urlpatterns = [
    path('', views.RegisteredDrugList.as_view(), name='DrugList'),
    path('drug/<str:reg_no>/match/', views.DrugDetailMatch.as_view(), name='DrugDetailMatch'),
    path('drug/<str:reg_no>/link/<int:cmsitem_id>/', views.LinkCMSItemModalView, name='LinkCMSItemModal'),
]
