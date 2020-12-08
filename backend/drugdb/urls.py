from django.urls import path
from . import views

app_name = 'drugdb'
urlpatterns = [
    path('', views.RegisteredDrugList.as_view(), name='DrugList'),
    # path('bill/<int:bill_id>/delivery/', views.BillDrugDeliveryView, name='BillDrugDeliveryView'),
    # path('bill/<int:bill_id>/delivery/add/<str:reg_no>/modal', views.BillDrugDeliveryAddDrugModal.as_view(), name='BillDrugDeliveryAddDrugModal'),
    # path('bill/<int:bill_id>/delivery/update/<str:reg_no>/modal', views.BillDrugDeliveryUpdateDrugModal.as_view(), name='BillDrugDeliveryUpdateDrugModal'),
    # path('bill/<int:bill_id>/delivery/choose_drug_modal', views.BillDrugDeliveryChooseDrugModal.as_view(), name='BillDrugDeliveryChooseDrugModal'),
    path('drug/<int:pk>', views.RegisteredDrugDetail.as_view(), name='DrugDetail'),
    path('delivery/', views.DrugDeliveryList.as_view(), name='DrugDeliveryList'),
    path('delivery/<int:pk>', views.DrugDeliveryDetail.as_view(), name='DrugDeliveryDetail'),
    # path('delivery/new/<str:reg_no>', views.NewDrugDelivery.as_view(), name='NewDrugDelivery'),
    # path('delivery/<int:pk>/update/', views.DrugDeliveryUpdate.as_view(), name='DrugDeliveryUpdate'),
    # path('delivery/<int:pk>/delete/', views.DrugDeliveryDelete.as_view(), name='DrugDeliveryDelete'),

]
